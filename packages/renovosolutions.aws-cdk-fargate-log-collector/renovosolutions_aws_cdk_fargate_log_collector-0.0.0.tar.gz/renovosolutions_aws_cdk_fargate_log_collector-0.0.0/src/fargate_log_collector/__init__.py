r'''
# cdk-library-fargate-log-collector

A Fargate service that collects logs from a list of specified files on an EFS access point and sends them to CloudWatch.
Only one task is run, because the agent is not designed to run in parallel.

There is a Lambda function included that restarts the agent service daily at 00:00 UTC.
This is to ensure that a new log stream is created every day for each log, named for the date,
with format `YYYY-MM-DD`. This is to make it easy to find the right log stream and
prevent the log streams from getting too large.

There are two defaults changed from the parent class:

* Deployment circuit breaker is enabled, with rollback, by default.
* minimum healthy percent is set to 0 by default, so we don't get a warning for having one task.

## Features

* Creates a task definition with a single container that runs the CloudWatch agent
* Accepts a list of files to collect logs from and what to do with them:

  * Allows passing existing log groups or creating new ones from passed properties, these may be mixed and matched
  * Allows passing neither log group nor log group properties, in which case a new log group will be created with a name based on the last part of the file path
  * Allows using the same log group configuration for multiple files
  * Allows specifying a regex pattern to find the start of a multiline log message
  * Allows specifying a regex pattern to include or exclude log messages that match the pattern
  * Allows specifying a timestamp format to parse the timestamp from the log message
  * Allows specifying a timezone to use when writing log events to CloudWatch
* Saves the agent state to an EFS access point, for restarts
* Grants itself read access to the logs and write access to the state access point
* Grants itself access to create log streams and put log events (but not create log groups)
* Creates a Lambda function that restarts the agent service daily at 00:00 UTC for a new log stream
* Allows configuration of most optional parameters for the Constructs used (see API document)
* Exposes the processed log mappings as a property for examination or reuse
* Exposes child Constructs as properties for examination or reuse
* May be imported using the parent class's static lookup methods

## API Doc

See [API](API.md)

## References

* [AWS Reference on CloudWatch Agent configuration file format](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Agent-Configuration-File-Details.html)

## Shortcomings

* The Lambda function that restarts the agent service is not currently configurable, it is hardcoded to run at 00:00 UTC. This seems adequate, because there is no point in restarting the agent when the date has not changed.
* The name of the log stream is not configurable, it is hardcoded to be the date in `YYYY-MM-DD` format. This aligns well with the daily restart of the agent service.
* Agent features not related to file collection are not currently supported. These mostly don't apply to running in a Fargate service.

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Examples

This construct requires some dependencies to instantiate:

* A stack with a definite environment (account and region)
* A VPC
* At least one EFS file system
* An EFS access point where the logs are read from
* An EFS access point where the agent state will be saved (may be on a different file system than the logs)
* A Fargate cluster to run on
* If you want to use existing log groups, you will need to create or look them up first

## Typescript (lots of extra options for illustration)

```python
import { Construct } from 'constructs';
import {
  Stack,
  StackProps,
  aws_ec2 as ec2,
  aws_ecs as ecs,
  aws_efs as efs,
  aws_logs as logs,
} from 'aws-cdk-lib';
import { FargateLogCollectorService } from '@renovosolutions/cdk-library-fargate-log-collector'

export class CdkExampleLogCollectorStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'MyVpc');

    const filesystem = new efs.FileSystem(this, 'MyEfsFileSystem', {
      vpc,
    });

    const logsAccessPoint = filesystem.addAccessPoint('logs', {
      path: '/var/log',
    });

    const stateAccessPoint = filesystem.addAccessPoint('state', {
      path: '/var/agent-state',
    });

    const cluster = new ecs.Cluster(this, 'MyCluster', {
      vpc,
      enableFargateCapacityProviders: true,
    });

    const logGroup = new logs.LogGroup(this, 'NewLogGroup', {
      logGroupName: 'new-log-group',
      retention: logs.RetentionDays.ONE_WEEK,
    });

    const serviceName = 'log-collector'; // this is the default value, but can be overridden

    new FargateLogCollectorService(this, 'FargateLogCollectorService', {
      logMappings: [
        {
          filePath: 'my-first-log-file.log',
          createLogGroup: { // this will create a new log group
            logGroupName: 'my-log-group',
            retention: logs.RetentionDays.TWO_YEARS,
          },
          multilinePattern: 'start-anchor', // this is a regex pattern that will be used to find the start of a multiline log message
        },
        {
          filePath: 'my-second-log-file.log',
          logGroup, // mix and match new with existing log groups
          timestampFormat: '%Y-%m-%d %H:%M:%S', // this is a format string that will be used to parse the timestamp from the log message
          timezone: 'UTC', // Use UTC time when writing log events to CloudWatch
        },
        {
          filePath: 'my-third-log-file.log',
          createLogGroup: {
            logGroupName: 'my-log-group', // this one is a duplicate, so it will reuse the matching log group from above
            retention: logs.RetentionDays.ONE_WEEK, // this will be ignored, because the log group already exists
          },
          filters: [
            {
              type: 'exclude',
              expression: 'SECRET', // this is a regex pattern that will be used to not forward log messages that match the pattern
            },
          ],
        },
        {
          filePath: 'my-fourth-log-file.log',
          createLogGroup: { // no name for this group, so it will be auto-generated
            retention: logs.RetentionDays.INFINITE, // other properties are still allowed without a name
          },
        },
        {
          filePath: 'my-fifth-log-file.log', // no log group config at all, so it will be auto-generated
        },
      ],
      efsLogsAccessPoint: logsAccessPoint,
      efsStateAccessPoint: stateAccessPoint,
      cluster,
      serviceName,
      agentCpu: 256, // the default value, but can be increased if you have a lot of logs
      agentMemory: 512, // the default value, but can be increased if you have a lot of logs
      containerLogging: ecs.LogDrivers.awsLogs({ // this is the default value, but can be overridden
        logGroup: new logs.LogGroup(this, 'ContainerLogGroup', {
          logGroupName: `/${cluster.clusterName}/${serviceName}/ecs/tasks`,
          retention: logs.RetentionDays.TWO_YEARS,
        }),
        streamPrefix: 'log-collector-task-logs',
        mode: ecs.AwsLogDriverMode.NON_BLOCKING,
        }),
      restartFunctionLogGroup: new logs.LogGroup(this, 'RestartServiceFunctionLogGroup', { // this is the default value, but can be overridden
        logGroupName: `/aws/lambda/${cluster.clusterName}/${serviceName}/restart-service`,
        retention: logs.RetentionDays.TWO_YEARS,
      }),
    });
  }
}
```

## Python (lots of extra options for illustration)

```python
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_efs as efs,
    aws_logs as logs,
)
from constructs import Construct
from fargate_log_collector import FargateLogCollectorService

class CdkExampleLogCollectorStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, 'MyVPC',)

        filesystem = efs.FileSystem(self, 'MyEfsFileSystem',
                                         vpc=vpc)

        logs_access_point = filesystem.add_access_point('logs', path='/var/log')

        state_access_point = filesystem.add_access_point('state', path='/var/agent-state')

        cluster = ecs.Cluster(self, 'MyCluster',
                              vpc=vpc,
                              enable_fargate_capacity_providers=True)

        log_group = logs.LogGroup(self, 'NewLogGroup',
                                  log_group_name='new-log-group',
                                  retention=logs.RetentionDays.ONE_WEEK)

        service_name = 'log-collector' # this is the default value, but can be overridden

        FargateLogCollectorService(self, 'FargateLogCollectorService',
                                   cluster=cluster,
                                   log_mappings=[
                                       {
                                           'filePath': 'my-first-log-file.log',
                                           'createLogGroup': { # this will create a new log group
                                               'logGroupName': 'my-log-group',
                                               'retention': logs.RetentionDays.TWO_YEARS,
                                           },
                                           'multilinePattern': 'start-anchor', # this is a regex pattern that will be used to find the start of a multiline log message
                                       },
                                       {
                                           'filePath': 'my-second-log-file.log',
                                           'logGroup': log_group, # mix and match new with existing log groups
                                           'timestampFormat': '%Y-%m-%d %H:%M:%S', # this is a format string that will be used to parse the timestamp from the log message
                                           'timezone': 'UTC', # Use UTC time when writing log events to CloudWatch
                                       },
                                       {
                                           'filePath': 'my-third-log-file.log',
                                           'createLogGroup': {
                                               'logGroupName': 'my-log-group', # this one is a duplicate, so it will reuse the matching log group from above
                                               'retention': logs.RetentionDays.ONE_WEEK, # this will be ignored, because the log group already exists
                                           },
                                           'filters': [
                                               {
                                                   'type': 'exclude',
                                                   'expression': 'SECRET', #
                                               },
                                           ],
                                       },
                                       {
                                           'filePath': 'my-fourth-log-file.log',
                                           'createLogGroup': {
                                               'retention': logs.RetentionDays.INFINITE, #
                                           },
                                       },
                                        {
                                            'filePath': 'my-fifth-log-file.log', # no log group config at all, so it will be auto-generated
                                        },
                                   ],
                                   efs_logs_access_point=logs_access_point,
                                   efs_state_access_point=state_access_point,
                                   service_name=service_name,
                                   agent_cpu=256, # the default value, but can be increased if you have a lot of logs
                                   agent_memory=512, # the default value, but can be increased if you have a lot of logs
                                   container_logging=ecs.LogDrivers.aws_logs( # this is the default value, but can be overridden
                                       log_group=logs.LogGroup(self, 'ContainerLogGroup',
                                                               log_group_name=f'/{cluster.cluster_name}/{service_name}/ecs/tasks',
                                                               retention=logs.RetentionDays.TWO_YEARS),
                                       stream_prefix='log-collector-task-logs',
                                       mode=ecs.AwsLogDriverMode.NON_BLOCKING),
                                   restart_function_log_group=logs.LogGroup(self, 'RestartServiceFunctionLogGroup', # this is the default value, but can be overridden
                                                                            log_group_name=f'/aws/lambda/{cluster.cluster_name}/{service_name}/restart-service',
                                                                            retention=logs.RetentionDays.TWO_YEARS))
```

## C Sharp (lots of extra options for illustration)

```csharp
using Amazon.CDK;
using EC2 = Amazon.CDK.AWS.EC2;
using EFS = Amazon.CDK.AWS.EFS;
using ECS = Amazon.CDK.AWS.ECS;
using Logs = Amazon.CDK.AWS.Logs;
using Constructs;
using renovosolutions;

namespace CsharpCdkTest
{
    public class CsharpCdkTestStack : Stack
    {
        internal CsharpCdkTestStack(Construct scope, string id, IStackProps props = null) : base(scope, id, props)
        {
            var vpc = new EC2.Vpc(this, "MyVpc");

            var filesystem = new EFS.FileSystem(this, "MyEfsFileSystem", new EFS.FileSystemProps
            {
                Vpc = vpc,
            });

            var logsAccessPoint = filesystem.AddAccessPoint("logs", new EFS.AccessPointOptions
            {
                Path = "/var/log",
            });

            var stateAccessPoint = filesystem.AddAccessPoint("state", new EFS.AccessPointOptions
            {
                Path = "/var/agent-state",
            });

            var cluster = new ECS.Cluster(this, "MyCluster", new ECS.ClusterProps
            {
                Vpc = vpc,
                EnableFargateCapacityProviders = true,
            });

            var logGroup = new Logs.LogGroup(this, "NewLogGroup", new Logs.LogGroupProps
            {
                LogGroupName = "new-log-group",
                Retention = Logs.RetentionDays.ONE_WEEK,
            });

            const string serviceName = "log-collector"; // this is the default value, but can be overridden

            new FargateLogCollectorService(this, "FargateLogCollectorService", new FargateLogCollectorServiceProps
            {
                LogMappings = new[]
                {
                    new LogMapping
                    {
                        FilePath = "my-first-log-file.log",
                        CreateLogGroup = new Logs.LogGroupProps // this will create a new log group
                        {
                            LogGroupName = "my-log-group",
                            Retention = Logs.RetentionDays.TWO_YEARS,
                        },
                        MultilinePattern = "start-anchor", // this is a regex pattern that will be used to find the start of a multiline log message
                    },
                    new LogMapping
                    {
                        FilePath = "my-second-log-file.log",
                        LogGroup = logGroup, // mix and match new with existing log groups
                        TimestampFormat = "%Y-%m-%d %H:%M:%S",
                        Timezone = "UTC",
                    },
                    new LogMapping
                    {
                        FilePath = "my-third-log-file.log",
                        CreateLogGroup = new Logs.LogGroupProps
                        {
                            LogGroupName = "my-log-group", // this one is a duplicate, so it will reuse the matching log group from above
                            Retention = Logs.RetentionDays.ONE_WEEK, // this will be ignored, because the log group already exists
                        },
                        Filters = new[]
                        {
                            new LogFilter
                            {
                                Type = "exclude",
                                Expression = "SECRET", // this is a regex pattern that will be used to not forward log messages that match the pattern
                            },
                        },
                    },
                    new LogMapping
                    {
                        FilePath = "my-fourth-log-file.log",
                        CreateLogGroup = new Logs.LogGroupProps
                        {
                            Retention = Logs.RetentionDays.INFINITE, // other properties are still allowed without a name
                        },
                    },
                    new LogMapping
                    {
                        FilePath = "my-fifth-log-file.log", // no log group config at all, so it will be auto-generated
                    },
                },
                EfsLogsAccessPoint = logsAccessPoint,
                EfsStateAccessPoint = stateAccessPoint,
                Cluster = cluster,
                ServiceName = serviceName,
                AgentCpu = 256, // the default value, but can be increased if you have a lot of logs
                AgentMemory = 512, // the default value, but can be increased if you have a lot of logs
                ContainerLogging = ECS.LogDrivers.AwsLogs(new ECS.AwsLogDriverProps // this is the default value, but can be overridden
                {
                    LogGroup = new Logs.LogGroup(this, "ContainerLogGroup", new Logs.LogGroupProps
                    {
                        LogGroupName = $"/{cluster.ClusterName}/{serviceName}/ecs/tasks",
                        Retention = Logs.RetentionDays.TWO_YEARS,
                    }),
                    StreamPrefix = "log-collector-task-logs",
                    Mode = ECS.AwsLogDriverMode.NON_BLOCKING,
                }),
                RestartFunctionLogGroup = new Logs.LogGroup(this, "RestartServiceFunctionLogGroup", new Logs.LogGroupProps // this is the default value, but can be overridden
                {
                    LogGroupName = $"/aws/lambda/{cluster.ClusterName}/{serviceName}/restart-service",
                    Retention = Logs.RetentionDays.TWO_YEARS,
                }),
            });
        }
    }
}
```

## Contributing

There is one interface generated by [`@mrgrain/jsii-struct-builder`](https://github.com/mrgrain/jsii-struct-builder).
This is the file `src/NarrowedFargateServiceProps.generated.ts`. If you need to change it, you can find the
configuration in the `.projenrc.ts` file. Simply running `npx projen` will regenerate the file.

We are using [`integ-runner`](https://docs.aws.amazon.com/cdk/api/v2/docs/integ-tests-alpha-readme.html) for integration
testing. The test is `test/integ.main.ts`. A snapshot comparison is run against the template from the last time the
the full test was run. This happens as part of the projen `test` task, which is also included in the `build` and
`release` tasks. If you change the code such that the template changes, you will need to run
`npx projen integ:update --profiles sandboxlab` to re-run the test and update the snapshot.
This takes about 20 minutes if everything goes well. Substitute `sandboxlab` with your profile name
if you need or want to run elsewhere. (Yes, it's `--profiles` and not `--profile`, because it's designed to run
against multiple profiles at once, but we only use one profile in this project.)
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_efs as _aws_cdk_aws_efs_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import constructs as _constructs_77d1e7e8


class FargateLogCollectorService(
    _aws_cdk_aws_ecs_ceddda9d.FargateService,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-fargate-log-collector.FargateLogCollectorService",
):
    '''A Fargate service that collects logs from a list of specified files on an EFS access point and sends them to CloudWatch.

    There is a single container in the task definition that runs the CloudWatch agent.

    There is a Lambda function included that restarts the agent service daily at 00:00 UTC.
    This is to ensure that a new log stream is created every day for each log, named for the date,
    with format ``YYYY-MM-DD``. This is to make it easy to find the right log stream and
    prevent the log streams from getting too large.

    There are two defaults changed from the parent class:

    - Deployment circuit breaker is enabled, with rollback, by default.
    - minimum healthy percent is set to 0 by default, so we don't get a warning for having one task.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
        efs_logs_access_point: _aws_cdk_aws_efs_ceddda9d.IAccessPoint,
        efs_state_access_point: _aws_cdk_aws_efs_ceddda9d.IAccessPoint,
        log_mappings: typing.Sequence[typing.Union["LogMapping", typing.Dict[builtins.str, typing.Any]]],
        agent_cpu: typing.Optional[jsii.Number] = None,
        agent_memory: typing.Optional[jsii.Number] = None,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        availability_zone_rebalancing: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.AvailabilityZoneRebalancing] = None,
        capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
        circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
        cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        container_logging: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LogDriver] = None,
        deployment_alarms: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentAlarmConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        max_healthy_percent: typing.Optional[jsii.Number] = None,
        min_healthy_percent: typing.Optional[jsii.Number] = None,
        platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
        propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        restart_function_log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        service_connect_configuration: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.ServiceConnectProps, typing.Dict[builtins.str, typing.Any]]] = None,
        service_name: typing.Optional[builtins.str] = None,
        task_definition_revision: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.TaskDefinitionRevision] = None,
        volume_configurations: typing.Optional[typing.Sequence[_aws_cdk_aws_ecs_ceddda9d.ServiceManagedVolume]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''The constructor for the FargateLogCollectorService.

        This creates the IAM task and execution roles for the task, the task definition,
        the CloudWatch agent container, the configuration for the agent, and the Fargate service.
        It also creates a Lambda function that restarts the agent service.

        :param scope: The scope in which to create this Construct. Normally this is a stack.
        :param id: The Construct ID of the service.
        :param cluster: The name of the cluster that hosts the service.
        :param efs_logs_access_point: The EFS access point where the logs are read from.
        :param efs_state_access_point: The EFS access point where the agent state is stored. This allows the agent to be restarted without losing its place in the logs. Otherwise, the agent would forward every log file from the start each time it is restarted. May be on a different EFS file system than ``efsLogsAccessPoint`` if desired.
        :param log_mappings: A list of log mappings. This is used to create the CloudWatch agent configuration. It is also used to create log groups if that is requested. At least one log mapping must be provided.
        :param agent_cpu: The amount of CPU units to allocate to the agent. 1024 CPU units = 1 vCPU. This is passed to the Fargate task definition. You might need to increase this if you have a lot of logs to process. Only some combinations of memory and CPU are valid. Default: 256
        :param agent_memory: The amount of memory (in MB) to allocate to the agent. This is passed to the Fargate task definition. You might need to increase this if you have a lot of logs to process. Only some combinations of memory and CPU are valid. Default: 512
        :param assign_public_ip: Specifies whether the task's elastic network interface receives a public IP address. If true, each task will receive a public IP address. Default: false
        :param availability_zone_rebalancing: Whether to use Availability Zone rebalancing for the service. If enabled, ``maxHealthyPercent`` must be greater than 100, and the service must not be a target of a Classic Load Balancer. Default: AvailabilityZoneRebalancing.DISABLED
        :param capacity_provider_strategies: A list of Capacity Provider strategies used to place a service. Default: - undefined
        :param circuit_breaker: Whether to enable the deployment circuit breaker. If this property is defined, circuit breaker will be implicitly enabled. Default: - disabled
        :param cloud_map_options: The options for configuring an Amazon ECS service to use service discovery. Default: - AWS Cloud Map service discovery is not enabled.
        :param container_logging: The logging configuration for the container. Default: ecs.LogDrivers.awsLogs({ logGroup: new logs.LogGroup(scope, 'ContainerLogGroup', { logGroupName: ``/${props.cluster.clusterName}/${props.serviceName || 'log-collector'}/ecs/tasks``, retention: logs.RetentionDays.TWO_YEARS, removalPolicy: RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE, }), streamPrefix: 'log-collector-task-logs', mode: ecs.AwsLogDriverMode.NON_BLOCKING, }),
        :param deployment_alarms: The alarm(s) to monitor during deployment, and behavior to apply if at least one enters a state of alarm during the deployment or bake time. Default: - No alarms will be monitored during deployment.
        :param deployment_controller: Specifies which deployment controller to use for the service. For more information, see `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_ Default: - Rolling update (ECS)
        :param enable_ecs_managed_tags: Specifies whether to enable Amazon ECS managed tags for the tasks within the service. For more information, see `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_ Default: false
        :param enable_execute_command: Whether to enable the ability to execute into a container. Default: - undefined
        :param health_check_grace_period: The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started. Default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        :param max_healthy_percent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: - 100 if daemon, otherwise 200
        :param min_healthy_percent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: - 0 if daemon, otherwise 50
        :param platform_version: The platform version on which to run your service. If one is not specified, the LATEST platform version is used by default. For more information, see `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_ in the Amazon Elastic Container Service Developer Guide. Default: Latest
        :param propagate_tags: Specifies whether to propagate the tags from the task definition or the service to the tasks in the service. Valid values are: PropagatedTagSource.SERVICE, PropagatedTagSource.TASK_DEFINITION or PropagatedTagSource.NONE Default: PropagatedTagSource.NONE
        :param restart_function_log_group: The log Group to use for the restart function. Default: new logs.LogGroup(this, 'RestartServiceFunctionLogGroup', { logGroupName: ``/aws/lambda/${props.cluster.clusterName}/${props.serviceName || 'log-collector'}/restart-service``, retention: logs.RetentionDays.TWO_YEARS, removalPolicy: RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE, }),
        :param security_groups: The security groups to associate with the service. If you do not specify a security group, a new security group is created. Default: - A new security group is created.
        :param service_connect_configuration: Configuration for Service Connect. Default: No ports are advertised via Service Connect on this service, and the service cannot make requests to other services via Service Connect.
        :param service_name: The name of the service. Default: - CloudFormation-generated name.
        :param task_definition_revision: Revision number for the task definition or ``latest`` to use the latest active task revision. Default: - Uses the revision of the passed task definition deployed by CloudFormation
        :param volume_configurations: Configuration details for a volume used by the service. This allows you to specify details about the EBS volume that can be attched to ECS tasks. Default: - undefined
        :param vpc_subnets: The subnets to associate with the service. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27e3b4c6413d4284e3a819fdd5fafebf8fa7eb7bf1ae8579ca897b60f94505bb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FargateLogCollectorServiceProps(
            cluster=cluster,
            efs_logs_access_point=efs_logs_access_point,
            efs_state_access_point=efs_state_access_point,
            log_mappings=log_mappings,
            agent_cpu=agent_cpu,
            agent_memory=agent_memory,
            assign_public_ip=assign_public_ip,
            availability_zone_rebalancing=availability_zone_rebalancing,
            capacity_provider_strategies=capacity_provider_strategies,
            circuit_breaker=circuit_breaker,
            cloud_map_options=cloud_map_options,
            container_logging=container_logging,
            deployment_alarms=deployment_alarms,
            deployment_controller=deployment_controller,
            enable_ecs_managed_tags=enable_ecs_managed_tags,
            enable_execute_command=enable_execute_command,
            health_check_grace_period=health_check_grace_period,
            max_healthy_percent=max_healthy_percent,
            min_healthy_percent=min_healthy_percent,
            platform_version=platform_version,
            propagate_tags=propagate_tags,
            restart_function_log_group=restart_function_log_group,
            security_groups=security_groups,
            service_connect_configuration=service_connect_configuration,
            service_name=service_name,
            task_definition_revision=task_definition_revision,
            volume_configurations=volume_configurations,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''Uniquely identifies this class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="agentCpu")
    def agent_cpu(self) -> jsii.Number:
        '''The amount of CPU units allocated to the agent.

        1024 CPU units = 1 vCPU.
        This was passed to the Fargate task definition.
        '''
        return typing.cast(jsii.Number, jsii.get(self, "agentCpu"))

    @builtins.property
    @jsii.member(jsii_name="agentMemory")
    def agent_memory(self) -> jsii.Number:
        '''The amount of memory (in MB) allocated to the agent.

        This was passed to the Fargate task definition.
        '''
        return typing.cast(jsii.Number, jsii.get(self, "agentMemory"))

    @builtins.property
    @jsii.member(jsii_name="efsLogsAccessPoint")
    def efs_logs_access_point(self) -> _aws_cdk_aws_efs_ceddda9d.IAccessPoint:
        '''The EFS access point where the logs are read from.'''
        return typing.cast(_aws_cdk_aws_efs_ceddda9d.IAccessPoint, jsii.get(self, "efsLogsAccessPoint"))

    @builtins.property
    @jsii.member(jsii_name="efsStateAccessPoint")
    def efs_state_access_point(self) -> _aws_cdk_aws_efs_ceddda9d.IAccessPoint:
        '''The EFS access point where the agent state is stored.

        This allows the agent to be restarted without losing its place in the logs.
        Otherwise, the agent would forward the whole logs each time it is restarted.
        '''
        return typing.cast(_aws_cdk_aws_efs_ceddda9d.IAccessPoint, jsii.get(self, "efsStateAccessPoint"))

    @builtins.property
    @jsii.member(jsii_name="logMappings")
    def log_mappings(self) -> typing.List["LogMapping"]:
        '''The list of log mappings, as processed from the input.

        This can be used to see how the input log mappings were understood.
        It is not the same as the log mappings passed in to the constructor.
        '''
        return typing.cast(typing.List["LogMapping"], jsii.get(self, "logMappings"))

    @builtins.property
    @jsii.member(jsii_name="restartFunction")
    def restart_function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        '''The Lambda function that restarts the agent service.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "restartFunction"))

    @builtins.property
    @jsii.member(jsii_name="restartScheduleRule")
    def restart_schedule_rule(self) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''The CloudWatch event rule that triggers the Lambda function to restart the agent service.

        It is set to run daily at 00:00 UTC. The purpose of this is to ensure that a new log stream
        is created every day, named for the date.
        '''
        return typing.cast(_aws_cdk_aws_events_ceddda9d.Rule, jsii.get(self, "restartScheduleRule"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-fargate-log-collector.FargateLogCollectorServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "efs_logs_access_point": "efsLogsAccessPoint",
        "efs_state_access_point": "efsStateAccessPoint",
        "log_mappings": "logMappings",
        "agent_cpu": "agentCpu",
        "agent_memory": "agentMemory",
        "assign_public_ip": "assignPublicIp",
        "availability_zone_rebalancing": "availabilityZoneRebalancing",
        "capacity_provider_strategies": "capacityProviderStrategies",
        "circuit_breaker": "circuitBreaker",
        "cloud_map_options": "cloudMapOptions",
        "container_logging": "containerLogging",
        "deployment_alarms": "deploymentAlarms",
        "deployment_controller": "deploymentController",
        "enable_ecs_managed_tags": "enableECSManagedTags",
        "enable_execute_command": "enableExecuteCommand",
        "health_check_grace_period": "healthCheckGracePeriod",
        "max_healthy_percent": "maxHealthyPercent",
        "min_healthy_percent": "minHealthyPercent",
        "platform_version": "platformVersion",
        "propagate_tags": "propagateTags",
        "restart_function_log_group": "restartFunctionLogGroup",
        "security_groups": "securityGroups",
        "service_connect_configuration": "serviceConnectConfiguration",
        "service_name": "serviceName",
        "task_definition_revision": "taskDefinitionRevision",
        "volume_configurations": "volumeConfigurations",
        "vpc_subnets": "vpcSubnets",
    },
)
class FargateLogCollectorServiceProps:
    def __init__(
        self,
        *,
        cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
        efs_logs_access_point: _aws_cdk_aws_efs_ceddda9d.IAccessPoint,
        efs_state_access_point: _aws_cdk_aws_efs_ceddda9d.IAccessPoint,
        log_mappings: typing.Sequence[typing.Union["LogMapping", typing.Dict[builtins.str, typing.Any]]],
        agent_cpu: typing.Optional[jsii.Number] = None,
        agent_memory: typing.Optional[jsii.Number] = None,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        availability_zone_rebalancing: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.AvailabilityZoneRebalancing] = None,
        capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
        circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
        cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        container_logging: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LogDriver] = None,
        deployment_alarms: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentAlarmConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        max_healthy_percent: typing.Optional[jsii.Number] = None,
        min_healthy_percent: typing.Optional[jsii.Number] = None,
        platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
        propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        restart_function_log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        service_connect_configuration: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.ServiceConnectProps, typing.Dict[builtins.str, typing.Any]]] = None,
        service_name: typing.Optional[builtins.str] = None,
        task_definition_revision: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.TaskDefinitionRevision] = None,
        volume_configurations: typing.Optional[typing.Sequence[_aws_cdk_aws_ecs_ceddda9d.ServiceManagedVolume]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Constructor properties for the FargateLogCollectorService.

        This uses the private NarrowedFargateServiceProps interface in this project as a base.

        :param cluster: The name of the cluster that hosts the service.
        :param efs_logs_access_point: The EFS access point where the logs are read from.
        :param efs_state_access_point: The EFS access point where the agent state is stored. This allows the agent to be restarted without losing its place in the logs. Otherwise, the agent would forward every log file from the start each time it is restarted. May be on a different EFS file system than ``efsLogsAccessPoint`` if desired.
        :param log_mappings: A list of log mappings. This is used to create the CloudWatch agent configuration. It is also used to create log groups if that is requested. At least one log mapping must be provided.
        :param agent_cpu: The amount of CPU units to allocate to the agent. 1024 CPU units = 1 vCPU. This is passed to the Fargate task definition. You might need to increase this if you have a lot of logs to process. Only some combinations of memory and CPU are valid. Default: 256
        :param agent_memory: The amount of memory (in MB) to allocate to the agent. This is passed to the Fargate task definition. You might need to increase this if you have a lot of logs to process. Only some combinations of memory and CPU are valid. Default: 512
        :param assign_public_ip: Specifies whether the task's elastic network interface receives a public IP address. If true, each task will receive a public IP address. Default: false
        :param availability_zone_rebalancing: Whether to use Availability Zone rebalancing for the service. If enabled, ``maxHealthyPercent`` must be greater than 100, and the service must not be a target of a Classic Load Balancer. Default: AvailabilityZoneRebalancing.DISABLED
        :param capacity_provider_strategies: A list of Capacity Provider strategies used to place a service. Default: - undefined
        :param circuit_breaker: Whether to enable the deployment circuit breaker. If this property is defined, circuit breaker will be implicitly enabled. Default: - disabled
        :param cloud_map_options: The options for configuring an Amazon ECS service to use service discovery. Default: - AWS Cloud Map service discovery is not enabled.
        :param container_logging: The logging configuration for the container. Default: ecs.LogDrivers.awsLogs({ logGroup: new logs.LogGroup(scope, 'ContainerLogGroup', { logGroupName: ``/${props.cluster.clusterName}/${props.serviceName || 'log-collector'}/ecs/tasks``, retention: logs.RetentionDays.TWO_YEARS, removalPolicy: RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE, }), streamPrefix: 'log-collector-task-logs', mode: ecs.AwsLogDriverMode.NON_BLOCKING, }),
        :param deployment_alarms: The alarm(s) to monitor during deployment, and behavior to apply if at least one enters a state of alarm during the deployment or bake time. Default: - No alarms will be monitored during deployment.
        :param deployment_controller: Specifies which deployment controller to use for the service. For more information, see `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_ Default: - Rolling update (ECS)
        :param enable_ecs_managed_tags: Specifies whether to enable Amazon ECS managed tags for the tasks within the service. For more information, see `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_ Default: false
        :param enable_execute_command: Whether to enable the ability to execute into a container. Default: - undefined
        :param health_check_grace_period: The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started. Default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        :param max_healthy_percent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: - 100 if daemon, otherwise 200
        :param min_healthy_percent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: - 0 if daemon, otherwise 50
        :param platform_version: The platform version on which to run your service. If one is not specified, the LATEST platform version is used by default. For more information, see `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_ in the Amazon Elastic Container Service Developer Guide. Default: Latest
        :param propagate_tags: Specifies whether to propagate the tags from the task definition or the service to the tasks in the service. Valid values are: PropagatedTagSource.SERVICE, PropagatedTagSource.TASK_DEFINITION or PropagatedTagSource.NONE Default: PropagatedTagSource.NONE
        :param restart_function_log_group: The log Group to use for the restart function. Default: new logs.LogGroup(this, 'RestartServiceFunctionLogGroup', { logGroupName: ``/aws/lambda/${props.cluster.clusterName}/${props.serviceName || 'log-collector'}/restart-service``, retention: logs.RetentionDays.TWO_YEARS, removalPolicy: RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE, }),
        :param security_groups: The security groups to associate with the service. If you do not specify a security group, a new security group is created. Default: - A new security group is created.
        :param service_connect_configuration: Configuration for Service Connect. Default: No ports are advertised via Service Connect on this service, and the service cannot make requests to other services via Service Connect.
        :param service_name: The name of the service. Default: - CloudFormation-generated name.
        :param task_definition_revision: Revision number for the task definition or ``latest`` to use the latest active task revision. Default: - Uses the revision of the passed task definition deployed by CloudFormation
        :param volume_configurations: Configuration details for a volume used by the service. This allows you to specify details about the EBS volume that can be attched to ECS tasks. Default: - undefined
        :param vpc_subnets: The subnets to associate with the service. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        '''
        if isinstance(circuit_breaker, dict):
            circuit_breaker = _aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker(**circuit_breaker)
        if isinstance(cloud_map_options, dict):
            cloud_map_options = _aws_cdk_aws_ecs_ceddda9d.CloudMapOptions(**cloud_map_options)
        if isinstance(deployment_alarms, dict):
            deployment_alarms = _aws_cdk_aws_ecs_ceddda9d.DeploymentAlarmConfig(**deployment_alarms)
        if isinstance(deployment_controller, dict):
            deployment_controller = _aws_cdk_aws_ecs_ceddda9d.DeploymentController(**deployment_controller)
        if isinstance(service_connect_configuration, dict):
            service_connect_configuration = _aws_cdk_aws_ecs_ceddda9d.ServiceConnectProps(**service_connect_configuration)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1bda54792d32f1f3f882d1f304562158065a52b23c25cb207cb1cbe42cf97a3)
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument efs_logs_access_point", value=efs_logs_access_point, expected_type=type_hints["efs_logs_access_point"])
            check_type(argname="argument efs_state_access_point", value=efs_state_access_point, expected_type=type_hints["efs_state_access_point"])
            check_type(argname="argument log_mappings", value=log_mappings, expected_type=type_hints["log_mappings"])
            check_type(argname="argument agent_cpu", value=agent_cpu, expected_type=type_hints["agent_cpu"])
            check_type(argname="argument agent_memory", value=agent_memory, expected_type=type_hints["agent_memory"])
            check_type(argname="argument assign_public_ip", value=assign_public_ip, expected_type=type_hints["assign_public_ip"])
            check_type(argname="argument availability_zone_rebalancing", value=availability_zone_rebalancing, expected_type=type_hints["availability_zone_rebalancing"])
            check_type(argname="argument capacity_provider_strategies", value=capacity_provider_strategies, expected_type=type_hints["capacity_provider_strategies"])
            check_type(argname="argument circuit_breaker", value=circuit_breaker, expected_type=type_hints["circuit_breaker"])
            check_type(argname="argument cloud_map_options", value=cloud_map_options, expected_type=type_hints["cloud_map_options"])
            check_type(argname="argument container_logging", value=container_logging, expected_type=type_hints["container_logging"])
            check_type(argname="argument deployment_alarms", value=deployment_alarms, expected_type=type_hints["deployment_alarms"])
            check_type(argname="argument deployment_controller", value=deployment_controller, expected_type=type_hints["deployment_controller"])
            check_type(argname="argument enable_ecs_managed_tags", value=enable_ecs_managed_tags, expected_type=type_hints["enable_ecs_managed_tags"])
            check_type(argname="argument enable_execute_command", value=enable_execute_command, expected_type=type_hints["enable_execute_command"])
            check_type(argname="argument health_check_grace_period", value=health_check_grace_period, expected_type=type_hints["health_check_grace_period"])
            check_type(argname="argument max_healthy_percent", value=max_healthy_percent, expected_type=type_hints["max_healthy_percent"])
            check_type(argname="argument min_healthy_percent", value=min_healthy_percent, expected_type=type_hints["min_healthy_percent"])
            check_type(argname="argument platform_version", value=platform_version, expected_type=type_hints["platform_version"])
            check_type(argname="argument propagate_tags", value=propagate_tags, expected_type=type_hints["propagate_tags"])
            check_type(argname="argument restart_function_log_group", value=restart_function_log_group, expected_type=type_hints["restart_function_log_group"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument service_connect_configuration", value=service_connect_configuration, expected_type=type_hints["service_connect_configuration"])
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument task_definition_revision", value=task_definition_revision, expected_type=type_hints["task_definition_revision"])
            check_type(argname="argument volume_configurations", value=volume_configurations, expected_type=type_hints["volume_configurations"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
            "efs_logs_access_point": efs_logs_access_point,
            "efs_state_access_point": efs_state_access_point,
            "log_mappings": log_mappings,
        }
        if agent_cpu is not None:
            self._values["agent_cpu"] = agent_cpu
        if agent_memory is not None:
            self._values["agent_memory"] = agent_memory
        if assign_public_ip is not None:
            self._values["assign_public_ip"] = assign_public_ip
        if availability_zone_rebalancing is not None:
            self._values["availability_zone_rebalancing"] = availability_zone_rebalancing
        if capacity_provider_strategies is not None:
            self._values["capacity_provider_strategies"] = capacity_provider_strategies
        if circuit_breaker is not None:
            self._values["circuit_breaker"] = circuit_breaker
        if cloud_map_options is not None:
            self._values["cloud_map_options"] = cloud_map_options
        if container_logging is not None:
            self._values["container_logging"] = container_logging
        if deployment_alarms is not None:
            self._values["deployment_alarms"] = deployment_alarms
        if deployment_controller is not None:
            self._values["deployment_controller"] = deployment_controller
        if enable_ecs_managed_tags is not None:
            self._values["enable_ecs_managed_tags"] = enable_ecs_managed_tags
        if enable_execute_command is not None:
            self._values["enable_execute_command"] = enable_execute_command
        if health_check_grace_period is not None:
            self._values["health_check_grace_period"] = health_check_grace_period
        if max_healthy_percent is not None:
            self._values["max_healthy_percent"] = max_healthy_percent
        if min_healthy_percent is not None:
            self._values["min_healthy_percent"] = min_healthy_percent
        if platform_version is not None:
            self._values["platform_version"] = platform_version
        if propagate_tags is not None:
            self._values["propagate_tags"] = propagate_tags
        if restart_function_log_group is not None:
            self._values["restart_function_log_group"] = restart_function_log_group
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if service_connect_configuration is not None:
            self._values["service_connect_configuration"] = service_connect_configuration
        if service_name is not None:
            self._values["service_name"] = service_name
        if task_definition_revision is not None:
            self._values["task_definition_revision"] = task_definition_revision
        if volume_configurations is not None:
            self._values["volume_configurations"] = volume_configurations
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def cluster(self) -> _aws_cdk_aws_ecs_ceddda9d.ICluster:
        '''The name of the cluster that hosts the service.'''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ICluster, result)

    @builtins.property
    def efs_logs_access_point(self) -> _aws_cdk_aws_efs_ceddda9d.IAccessPoint:
        '''The EFS access point where the logs are read from.'''
        result = self._values.get("efs_logs_access_point")
        assert result is not None, "Required property 'efs_logs_access_point' is missing"
        return typing.cast(_aws_cdk_aws_efs_ceddda9d.IAccessPoint, result)

    @builtins.property
    def efs_state_access_point(self) -> _aws_cdk_aws_efs_ceddda9d.IAccessPoint:
        '''The EFS access point where the agent state is stored.

        This allows the agent to be restarted without losing its place in the logs.
        Otherwise, the agent would forward every log file from the start
        each time it is restarted.

        May be on a different EFS file system than ``efsLogsAccessPoint`` if desired.
        '''
        result = self._values.get("efs_state_access_point")
        assert result is not None, "Required property 'efs_state_access_point' is missing"
        return typing.cast(_aws_cdk_aws_efs_ceddda9d.IAccessPoint, result)

    @builtins.property
    def log_mappings(self) -> typing.List["LogMapping"]:
        '''A list of log mappings.

        This is used to create the CloudWatch agent configuration.
        It is also used to create log groups if that is requested.
        At least one log mapping must be provided.
        '''
        result = self._values.get("log_mappings")
        assert result is not None, "Required property 'log_mappings' is missing"
        return typing.cast(typing.List["LogMapping"], result)

    @builtins.property
    def agent_cpu(self) -> typing.Optional[jsii.Number]:
        '''The amount of CPU units to allocate to the agent.

        1024 CPU units = 1 vCPU.
        This is passed to the Fargate task definition.
        You might need to increase this if you have a lot of logs to process.
        Only some combinations of memory and CPU are valid.

        :default: 256

        :see: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.TaskDefinition.html#memorymib
        '''
        result = self._values.get("agent_cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def agent_memory(self) -> typing.Optional[jsii.Number]:
        '''The amount of memory (in MB) to allocate to the agent.

        This is passed to the Fargate task definition.
        You might need to increase this if you have a lot of logs to process.
        Only some combinations of memory and CPU are valid.

        :default: 512

        :see: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.TaskDefinition.html#cpu
        '''
        result = self._values.get("agent_memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def assign_public_ip(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether the task's elastic network interface receives a public IP address.

        If true, each task will receive a public IP address.

        :default: false
        '''
        result = self._values.get("assign_public_ip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def availability_zone_rebalancing(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.AvailabilityZoneRebalancing]:
        '''Whether to use Availability Zone rebalancing for the service.

        If enabled, ``maxHealthyPercent`` must be greater than 100, and the service must not be a target
        of a Classic Load Balancer.

        :default: AvailabilityZoneRebalancing.DISABLED
        '''
        result = self._values.get("availability_zone_rebalancing")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.AvailabilityZoneRebalancing], result)

    @builtins.property
    def capacity_provider_strategies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy]]:
        '''A list of Capacity Provider strategies used to place a service.

        :default: - undefined
        '''
        result = self._values.get("capacity_provider_strategies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy]], result)

    @builtins.property
    def circuit_breaker(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker]:
        '''Whether to enable the deployment circuit breaker.

        If this property is defined, circuit breaker will be implicitly
        enabled.

        :default: - disabled
        '''
        result = self._values.get("circuit_breaker")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker], result)

    @builtins.property
    def cloud_map_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions]:
        '''The options for configuring an Amazon ECS service to use service discovery.

        :default: - AWS Cloud Map service discovery is not enabled.
        '''
        result = self._values.get("cloud_map_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions], result)

    @builtins.property
    def container_logging(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LogDriver]:
        '''The logging configuration for the container.

        :default:

        ecs.LogDrivers.awsLogs({
        logGroup: new logs.LogGroup(scope, 'ContainerLogGroup', {
        logGroupName: ``/${props.cluster.clusterName}/${props.serviceName || 'log-collector'}/ecs/tasks``,
        retention: logs.RetentionDays.TWO_YEARS,
        removalPolicy: RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE,
        }),
        streamPrefix: 'log-collector-task-logs',
        mode: ecs.AwsLogDriverMode.NON_BLOCKING,
        }),
        '''
        result = self._values.get("container_logging")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LogDriver], result)

    @builtins.property
    def deployment_alarms(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentAlarmConfig]:
        '''The alarm(s) to monitor during deployment, and behavior to apply if at least one enters a state of alarm during the deployment or bake time.

        :default: - No alarms will be monitored during deployment.
        '''
        result = self._values.get("deployment_alarms")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentAlarmConfig], result)

    @builtins.property
    def deployment_controller(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentController]:
        '''Specifies which deployment controller to use for the service.

        For more information, see
        `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_

        :default: - Rolling update (ECS)
        '''
        result = self._values.get("deployment_controller")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentController], result)

    @builtins.property
    def enable_ecs_managed_tags(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether to enable Amazon ECS managed tags for the tasks within the service.

        For more information, see
        `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_

        :default: false
        '''
        result = self._values.get("enable_ecs_managed_tags")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_execute_command(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable the ability to execute into a container.

        :default: - undefined
        '''
        result = self._values.get("enable_execute_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def health_check_grace_period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started.

        :default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        '''
        result = self._values.get("health_check_grace_period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def max_healthy_percent(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment.

        :default: - 100 if daemon, otherwise 200
        '''
        result = self._values.get("max_healthy_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_healthy_percent(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment.

        :default: - 0 if daemon, otherwise 50
        '''
        result = self._values.get("min_healthy_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def platform_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion]:
        '''The platform version on which to run your service.

        If one is not specified, the LATEST platform version is used by default. For more information, see
        `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_
        in the Amazon Elastic Container Service Developer Guide.

        :default: Latest
        '''
        result = self._values.get("platform_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion], result)

    @builtins.property
    def propagate_tags(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource]:
        '''Specifies whether to propagate the tags from the task definition or the service to the tasks in the service.

        Valid values are: PropagatedTagSource.SERVICE, PropagatedTagSource.TASK_DEFINITION or PropagatedTagSource.NONE

        :default: PropagatedTagSource.NONE
        '''
        result = self._values.get("propagate_tags")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource], result)

    @builtins.property
    def restart_function_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The log Group to use for the restart function.

        :default:

        new logs.LogGroup(this, 'RestartServiceFunctionLogGroup', {
        logGroupName: ``/aws/lambda/${props.cluster.clusterName}/${props.serviceName || 'log-collector'}/restart-service``,
        retention: logs.RetentionDays.TWO_YEARS,
        removalPolicy: RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE,
        }),
        '''
        result = self._values.get("restart_function_log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The security groups to associate with the service.

        If you do not specify a security group, a new security group is created.

        :default: - A new security group is created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def service_connect_configuration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ServiceConnectProps]:
        '''Configuration for Service Connect.

        :default:

        No ports are advertised via Service Connect on this service, and the service
        cannot make requests to other services via Service Connect.
        '''
        result = self._values.get("service_connect_configuration")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ServiceConnectProps], result)

    @builtins.property
    def service_name(self) -> typing.Optional[builtins.str]:
        '''The name of the service.

        :default: - CloudFormation-generated name.
        '''
        result = self._values.get("service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def task_definition_revision(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.TaskDefinitionRevision]:
        '''Revision number for the task definition or ``latest`` to use the latest active task revision.

        :default: - Uses the revision of the passed task definition deployed by CloudFormation
        '''
        result = self._values.get("task_definition_revision")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.TaskDefinitionRevision], result)

    @builtins.property
    def volume_configurations(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.ServiceManagedVolume]]:
        '''Configuration details for a volume used by the service.

        This allows you to specify
        details about the EBS volume that can be attched to ECS tasks.

        :default: - undefined
        '''
        result = self._values.get("volume_configurations")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.ServiceManagedVolume]], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets to associate with the service.

        :default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargateLogCollectorServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-fargate-log-collector.LogFilter",
    jsii_struct_bases=[],
    name_mapping={"expression": "expression", "type": "type"},
)
class LogFilter:
    def __init__(self, *, expression: builtins.str, type: builtins.str) -> None:
        '''A filter entry for a log.

        :param expression: The filter pattern. This is a regular expression that matches the log lines to include or exclude.
        :param type: The type of filter. Either 'include' or 'exclude'.

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Agent-Configuration-File-Details.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6630e44bca6f7a06c4709f661245e6d606c66bccb517fde835b407ab1f38f6d)
            check_type(argname="argument expression", value=expression, expected_type=type_hints["expression"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "expression": expression,
            "type": type,
        }

    @builtins.property
    def expression(self) -> builtins.str:
        '''The filter pattern.

        This is a regular expression that matches the log lines to include or exclude.
        '''
        result = self._values.get("expression")
        assert result is not None, "Required property 'expression' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of filter.

        Either 'include' or 'exclude'.
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LogFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-fargate-log-collector.LogMapping",
    jsii_struct_bases=[],
    name_mapping={
        "file_path": "filePath",
        "create_log_group": "createLogGroup",
        "filters": "filters",
        "log_group": "logGroup",
        "multiline_pattern": "multilinePattern",
        "timestamp_format": "timestampFormat",
        "timezone": "timezone",
    },
)
class LogMapping:
    def __init__(
        self,
        *,
        file_path: builtins.str,
        create_log_group: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
        filters: typing.Optional[typing.Sequence[typing.Union[LogFilter, typing.Dict[builtins.str, typing.Any]]]] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        multiline_pattern: typing.Optional[builtins.str] = None,
        timestamp_format: typing.Optional[builtins.str] = None,
        timezone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''A mapping of a log file to a CloudWatch log group.

        :param file_path: The path to the log file on the EFS access point. This should be a relative path from the root of the access point. It must not start with a '/'.
        :param create_log_group: The props for a log group to create. Do not pass props for an existing log group here, or a duplicate will be created and you will get a deployment failure. If both ``createLogGroup`` and ``logGroup`` are absent, a new log group will be created with a name derived from last part of the file path and default props. If both ``createLogGroup`` and ``logGroup`` are provided, the ``logGroup`` will be used, and the ``createLogGroup`` will be ignored. Default: - None
        :param filters: A list of filters to apply to the log file. Each filter is a regular expression that matches the log lines to include or exclude. If you include this field, the agent processes each log message with all of the filters that you specify, and only the log events that pass all of the filters are published to CloudWatch Logs. The log entries that don’t pass all of the filters will still remain in the host's log file, but will not be sent to CloudWatch Logs. If you omit this field, all logs in the log file are published to CloudWatch Logs.
        :param log_group: The log group to use. This should be an existing log group. If both ``createLogGroup`` and ``logGroup`` are provided, the ``logGroup`` will be used, and the ``createLogGroup`` will be ignored. Default: - None
        :param multiline_pattern: The pattern to use for recognizing multi-line log messages. This is a regular expression that matches the start of a new log message. If this is not provided, the agent will treat each line that begins with a non-whitespace character as starting a new log message. If you include this field, you can specify ``{timestamp_format}`` to use the same regular expression as your timestamp format. Otherwise, you can specify a different regular expression for CloudWatch Logs to use to determine the start lines of multi-line entries. Default: - None
        :param timestamp_format: The format of the timestamp in the log file. This is not quite the same as a strftime format string. If this is not provided, the agent will forward all messages with a timestamp matching the time it sees the message. Default: - None
        :param timezone: Whether to use UTC or local time for messages added to the log group. Either 'UTC' or 'Local'. It does not allow arbitrary timezones to be set. This is only used if ``timestampFormat`` is provided. If this is not provided, the agent will use local time. Default: - None
        '''
        if isinstance(create_log_group, dict):
            create_log_group = _aws_cdk_aws_logs_ceddda9d.LogGroupProps(**create_log_group)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be57c40e962bf3e069dfb7fd90dfd30b3dec83638015c6ad1d84183ab0936b4f)
            check_type(argname="argument file_path", value=file_path, expected_type=type_hints["file_path"])
            check_type(argname="argument create_log_group", value=create_log_group, expected_type=type_hints["create_log_group"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument multiline_pattern", value=multiline_pattern, expected_type=type_hints["multiline_pattern"])
            check_type(argname="argument timestamp_format", value=timestamp_format, expected_type=type_hints["timestamp_format"])
            check_type(argname="argument timezone", value=timezone, expected_type=type_hints["timezone"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "file_path": file_path,
        }
        if create_log_group is not None:
            self._values["create_log_group"] = create_log_group
        if filters is not None:
            self._values["filters"] = filters
        if log_group is not None:
            self._values["log_group"] = log_group
        if multiline_pattern is not None:
            self._values["multiline_pattern"] = multiline_pattern
        if timestamp_format is not None:
            self._values["timestamp_format"] = timestamp_format
        if timezone is not None:
            self._values["timezone"] = timezone

    @builtins.property
    def file_path(self) -> builtins.str:
        '''The path to the log file on the EFS access point.

        This should be a relative path from the root of the access point.
        It must not start with a '/'.

        Example::

            'my-log-file.log' if the main service mounts the logs access point at '/mnt/logs' and the file is at '/mnt/logs/my-log-file.log'. 'logs/my-log-file.log' if the main service mounts the logs access point at '/opt/app' and the file is at '/opt/app/logs/my-log-file.log/'.
        '''
        result = self._values.get("file_path")
        assert result is not None, "Required property 'file_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def create_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupProps]:
        '''The props for a log group to create.

        Do not pass props for an existing log group here,
        or a duplicate will be created and you will get
        a deployment failure.

        If both ``createLogGroup`` and ``logGroup`` are absent,
        a new log group will be created with a name
        derived from last part of the file path
        and default props.

        If both ``createLogGroup`` and ``logGroup`` are provided,
        the ``logGroup`` will be used, and the ``createLogGroup`` will be ignored.

        :default: - None
        '''
        result = self._values.get("create_log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupProps], result)

    @builtins.property
    def filters(self) -> typing.Optional[typing.List[LogFilter]]:
        '''A list of filters to apply to the log file.

        Each filter is a regular expression that matches the log lines to include or exclude.
        If you include this field, the agent processes each log message with all of the
        filters that you specify, and only the log events that pass all of the filters
        are published to CloudWatch Logs. The log entries that don’t pass all of the
        filters will still remain in the host's log file, but will not be sent to CloudWatch Logs.
        If you omit this field, all logs in the log file are published to CloudWatch Logs.
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional[typing.List[LogFilter]], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The log group to use.

        This should be an existing log group.

        If both ``createLogGroup`` and ``logGroup`` are provided,
        the ``logGroup`` will be used, and the ``createLogGroup`` will be ignored.

        :default: - None
        '''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def multiline_pattern(self) -> typing.Optional[builtins.str]:
        '''The pattern to use for recognizing multi-line log messages.

        This is a regular expression that matches the start of a new log message.
        If this is not provided, the agent will treat each line that begins with
        a non-whitespace character as starting a new log message.
        If you include this field, you can specify ``{timestamp_format}`` to use
        the same regular expression as your timestamp format. Otherwise, you can
        specify a different regular expression for CloudWatch Logs to use to determine
        the start lines of multi-line entries.

        :default: - None
        '''
        result = self._values.get("multiline_pattern")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timestamp_format(self) -> typing.Optional[builtins.str]:
        '''The format of the timestamp in the log file.

        This is not quite the same as a strftime format string.
        If this is not provided, the agent will forward all messages
        with a timestamp matching the time it sees the message.

        :default: - None
        '''
        result = self._values.get("timestamp_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timezone(self) -> typing.Optional[builtins.str]:
        '''Whether to use UTC or local time for messages added to the log group.

        Either 'UTC' or 'Local'. It does not allow arbitrary timezones to be set.
        This is only used if ``timestampFormat`` is provided.
        If this is not provided, the agent will use local time.

        :default: - None
        '''
        result = self._values.get("timezone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LogMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "FargateLogCollectorService",
    "FargateLogCollectorServiceProps",
    "LogFilter",
    "LogMapping",
]

publication.publish()

def _typecheckingstub__27e3b4c6413d4284e3a819fdd5fafebf8fa7eb7bf1ae8579ca897b60f94505bb(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
    efs_logs_access_point: _aws_cdk_aws_efs_ceddda9d.IAccessPoint,
    efs_state_access_point: _aws_cdk_aws_efs_ceddda9d.IAccessPoint,
    log_mappings: typing.Sequence[typing.Union[LogMapping, typing.Dict[builtins.str, typing.Any]]],
    agent_cpu: typing.Optional[jsii.Number] = None,
    agent_memory: typing.Optional[jsii.Number] = None,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    availability_zone_rebalancing: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.AvailabilityZoneRebalancing] = None,
    capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
    circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
    cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    container_logging: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LogDriver] = None,
    deployment_alarms: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentAlarmConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
    enable_execute_command: typing.Optional[builtins.bool] = None,
    health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    max_healthy_percent: typing.Optional[jsii.Number] = None,
    min_healthy_percent: typing.Optional[jsii.Number] = None,
    platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
    propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
    restart_function_log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    service_connect_configuration: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.ServiceConnectProps, typing.Dict[builtins.str, typing.Any]]] = None,
    service_name: typing.Optional[builtins.str] = None,
    task_definition_revision: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.TaskDefinitionRevision] = None,
    volume_configurations: typing.Optional[typing.Sequence[_aws_cdk_aws_ecs_ceddda9d.ServiceManagedVolume]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1bda54792d32f1f3f882d1f304562158065a52b23c25cb207cb1cbe42cf97a3(
    *,
    cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
    efs_logs_access_point: _aws_cdk_aws_efs_ceddda9d.IAccessPoint,
    efs_state_access_point: _aws_cdk_aws_efs_ceddda9d.IAccessPoint,
    log_mappings: typing.Sequence[typing.Union[LogMapping, typing.Dict[builtins.str, typing.Any]]],
    agent_cpu: typing.Optional[jsii.Number] = None,
    agent_memory: typing.Optional[jsii.Number] = None,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    availability_zone_rebalancing: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.AvailabilityZoneRebalancing] = None,
    capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
    circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
    cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    container_logging: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LogDriver] = None,
    deployment_alarms: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentAlarmConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
    enable_execute_command: typing.Optional[builtins.bool] = None,
    health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    max_healthy_percent: typing.Optional[jsii.Number] = None,
    min_healthy_percent: typing.Optional[jsii.Number] = None,
    platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
    propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
    restart_function_log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    service_connect_configuration: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.ServiceConnectProps, typing.Dict[builtins.str, typing.Any]]] = None,
    service_name: typing.Optional[builtins.str] = None,
    task_definition_revision: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.TaskDefinitionRevision] = None,
    volume_configurations: typing.Optional[typing.Sequence[_aws_cdk_aws_ecs_ceddda9d.ServiceManagedVolume]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6630e44bca6f7a06c4709f661245e6d606c66bccb517fde835b407ab1f38f6d(
    *,
    expression: builtins.str,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be57c40e962bf3e069dfb7fd90dfd30b3dec83638015c6ad1d84183ab0936b4f(
    *,
    file_path: builtins.str,
    create_log_group: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    filters: typing.Optional[typing.Sequence[typing.Union[LogFilter, typing.Dict[builtins.str, typing.Any]]]] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    multiline_pattern: typing.Optional[builtins.str] = None,
    timestamp_format: typing.Optional[builtins.str] = None,
    timezone: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
