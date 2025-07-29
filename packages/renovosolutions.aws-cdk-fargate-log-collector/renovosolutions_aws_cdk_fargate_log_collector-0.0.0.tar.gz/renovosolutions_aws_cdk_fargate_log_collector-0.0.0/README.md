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
