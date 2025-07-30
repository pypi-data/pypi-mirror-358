# cdk-library-crowdstrike-ingestion

A CDK library to ease repetitive construct creation for CrowdStrike data ingestion.

This library provides a construct that creates an S3 bucket with the necessary configuration for CrowdStrike data ingestion, along with an SQS queue for notifications, an IAM role for access, and optionally a KMS key for encryption.

It also provides another construct that handles creating log group subscriptions to a central bucket, along with the role needed for CloudWatch Logs to create the subscription.

## Features

### CrowdStrike Bucket Construct

* Creates an S3 bucket with appropriate security settings for CrowdStrike data ingestion
* Creates an SQS queue for bucket notifications with a dead-letter queue
* Creates an IAM role that CrowdStrike can assume to access the data
* Optionally creates a KMS key for encrypting data (to use if the service generating the data wants it)
* Reads external ID from SSM parameter
* Supports organization-wide access for multi-account setups
* Configures bucket policies for logging if needed
* Provides customization options for all resources

### Log Group Subscription Construct

* Creates a CloudWatch Log Group Subscription to forward logs to a central S3 bucket
* Automatically creates the necessary IAM role for CloudWatch Logs to create the subscription
* Supports passing in an existing role if desired
* Allows customization of the filter pattern for the subscription

## API Doc

See [API](API.md)

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Examples

### TypeScript

```python
import { Stack, StackProps, Duration, aws_iam as iam, aws_logs as logs } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { CrowdStrikeBucket, CrowdStrikeLogSubscription } from '@renovosolutions/cdk-library-crowdstrike-ingestion';

export class CrowdStrikeIngestionStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // Basic usage with default settings
    new CrowdStrikeBucket(this, 'BasicBucket', {
      bucketName: 'my-crowdstrike-bucket',
      crowdStrikeRoleArn: 'arn:aws:ssm:us-east-1:123456789012:parameter/custom/crowdstrike/roleArn',
      crowdStrikeExternalIdParameterArn: 'arn:aws:ssm:us-east-1:123456789012:parameter/custom/crowdstrike/externalId',
    });

    // Advanced usage with KMS key and organization access
    new CrowdStrikeBucket(this, 'AdvancedBucket', {
      bucketName: 'my-advanced-crowdstrike-bucket',
      createKmsKey: true,
      keyProps: {
        alias: 'crowdstrike-key',
        enableKeyRotation: true,
        description: 'KMS Key for CrowdStrike data encryption',
      },
      queueProps: {
        queueName: 'crowdstrike-notifications',
        visibilityTimeout: Duration.seconds(300),
      },
      roleProps: {
        roleName: 'crowdstrike-access-role',
        assumedBy: new iam.PrincipalWithConditions(new iam.ArnPrincipal('arn:aws:iam::123456789012:role/CrowdStrikeRole'), {
          StringEquals: {
            'sts:ExternalId': 'externalId123',
          },
        }),
      },
      loggingBucketSourceName: 'my-logging-bucket', // Allow this bucket to send access logs
      orgId: 'o-1234567', // Allow all accounts in the organization to write to the bucket    });

    // Example of creating a log group subscription
    const logGroup = new aws_logs.LogGroup(this, 'MyLogGroup', {
      logGroupName: 'my-log-group',
    });

    const subscription = new CrowdStrikeLogSubscription(stack, 'BasicTestSubscription', {
      logGroup,
      logDestinationArn: 'arn:aws:logs:us-east-1:123456789012:destination:test-destination',
    });

    new CrowdStrikeLogSubscription(stack, 'AdvancedTestSubscription', {
      logGroup,
      logDestinationArn: 'arn:aws:logs:us-east-1:123456789012:destination:another-test-destination',
      role: subscription.role,
      filterPattern: 'error',
    });
  }
}
```

### Python

```python
from aws_cdk import (
    Stack,
    Duration,
    aws_iam as iam,
    aws_kms as kms,
    aws_logs as logs,
)
from constructs import Construct
from crowdstrike_ingestion import ( CrowdStrikeBucket, CrowdStrikeLogSubscription )

class CrowdStrikeIngestionStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Basic usage with default settings
        CrowdStrikeBucket(self, 'BasicBucket',
            bucket_name='my-crowdstrike-bucket',
            crowd_strike_role_arn='arn:aws:ssm:us-east-1:123456789012:parameter/custom/crowdstrike/roleArn',            crowd_strike_external_id_parameter_arn='arn:aws:ssm:us-east-1:123456789012:parameter/custom/crowdstrike/externalId')

        # Advanced usage with KMS key and organization access
        CrowdStrikeBucket(self, 'AdvancedBucket',
            bucket_name='my-advanced-crowdstrike-bucket',
            create_kms_key=True,
            key_props={
                alias='crowdstrike-key',
                enable_key_rotation=True,
                description='KMS Key for CrowdStrike data encryption'
            },
            queue_props={
                'queue_name': 'crowdstrike-notifications',
                'visibility_timeout': Duration.seconds(300)
            },
            role_props={
                'role_name': 'crowdstrike-access-role',
                'assumed_by': iam.PrincipalWithConditions(
                    iam.ArnPrincipal('arn:aws:iam::123456789012:role/CrowdStrikeRole'),
                    {'StringEquals': {'sts:ExternalId': 'externalId123'}})
            },
            logging_bucket_source_name='my-logging-bucket',  # Allow this bucket to send access logs
            org_id='o-1234567')  # Allow all accounts in the organization to write to the bucket
        # Example of creating a log group subscription
        log_group = logs.LogGroup(self, 'MyLogGroup', log_group_name='my-log-group')

        subscription = CrowdStrikeLogSubscription(self, 'BasicTestSubscription',
            log_group=log_group,
            log_destination_arn='arn:aws:logs:us-east-1:123456789012:destination:test-destination')

        CrowdStrikeLogSubscription(self, 'AdvancedTestSubscription',
            log_group=log_group,
            log_destination_arn='arn:aws:logs:us-east-1:123456789012:destination:another-test-destination',
            role=subscription.role,
            filter_pattern='error')
```

### C Sharp

```csharp
using Amazon.CDK;
using IAM = Amazon.CDK.AWS.IAM;
using KMS = Amazon.CDK.AWS.KMS;
using Logs = Amazon.CDK.AWS.Logs;
using SQS = Amazon.CDK.AWS.SQS;
using Constructs;
using System.Collections.Generic;
using renovosolutions;

namespace CrowdStrikeIngestionExample
{
    public class CrowdStrikeIngestionStack : Stack
    {
        internal CrowdStrikeIngestionStack(Construct scope, string id, IStackProps props = null) : base(scope, id, props)
        {
            // Basic usage with default settings
            new CrowdStrikeBucket(this, "BasicBucket", new CrowdStrikeBucketProps
            {
                BucketName = "my-crowdstrike-bucket",
                CrowdStrikeRoleArn = "arn:aws:ssm:us-east-1:123456789012:parameter/custom/crowdstrike/roleArn",                CrowdStrikeExternalIdParameterArn = "arn:aws:ssm:us-east-1:123456789012:parameter/custom/crowdstrike/externalId"
            });

            // Advanced usage with KMS key and organization access
            new CrowdStrikeBucket(this, "AdvancedBucket", new CrowdStrikeBucketProps
            {
                BucketName = "my-advanced-crowdstrike-bucket",
                CreateKmsKey = true,
                KeyProps = new KMS.KeyProps
                {
                    Alias = "crowdstrike-key",
                    EnableKeyRotation = true,
                    Description = "KMS Key for CrowdStrike data encryption"
                },
                QueueProps = new SQS.QueueProps
                {
                    QueueName = "crowdstrike-notifications",
                    VisibilityTimeout = Duration.Seconds(300)
                },
                RoleProps = new IAM.RoleProps
                {
                    RoleName = "crowdstrike-access-role"
                    AssumedBy = new IAM.PrincipalWithConditions(new IAM.ArnPrincipal("arn:aws:iam::123456789012:role/CrowdStrikeRole"), new Dictionary<string, object>
                    {
                        { "StringEquals", new Dictionary<string, string> { { "sts:ExternalId", "externalId123" } } }
                    })
                },
                LoggingBucketSourceName = "my-logging-bucket", // Allow this bucket to send access logs
                OrgId = "o-1234567" // Allow all accounts in the organization to write to the bucket            });

            // Example of creating a log group subscription
            var logGroup = new Logs.LogGroup(this, "MyLogGroup", new Logs.LogGroupProps
            {
                LogGroupName = "my-log-group"
            });

            var subscription = new CrowdStrikeLogSubscription(this, "BasicTestSubscription", new CrowdStrikeLogSubscriptionProps
            {
                LogGroup = logGroup,
                LogDestinationArn = "arn:aws:logs:us-east-1:123456789012:destination:test-destination"
            });

            new CrowdStrikeLogSubscription(this, "AdvancedTestSubscription", new CrowdStrikeLogSubscriptionProps
            {
                LogGroup = logGroup,
                LogDestinationArn = "arn:aws:logs:us-east-1:123456789012:destination:another-test-destination",
                Role = subscription.Role,
                FilterPattern = "error"
            });
        }
    }
}
```
