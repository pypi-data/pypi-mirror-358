r'''
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
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_ceddda9d
import constructs as _constructs_77d1e7e8


class CrowdStrikeBucket(
    _aws_cdk_aws_s3_ceddda9d.Bucket,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-crowdstrike-ingestion.CrowdStrikeBucket",
):
    '''A construct that creates an S3 bucket for CrowdStrike data ingestion, along with an SQS queue for notifications, an IAM role for access, and optionally a KMS key for encryption.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        create_kms_key: typing.Optional[builtins.bool] = None,
        crowd_strike_external_id_parameter_arn: typing.Optional[builtins.str] = None,
        crowd_strike_role_arn: typing.Optional[builtins.str] = None,
        key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        logging_bucket_source_name: typing.Optional[builtins.str] = None,
        org_id: typing.Optional[builtins.str] = None,
        queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
        role_props: typing.Optional[typing.Union[_aws_cdk_aws_iam_ceddda9d.RoleProps, typing.Dict[builtins.str, typing.Any]]] = None,
        access_control: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl] = None,
        auto_delete_objects: typing.Optional[builtins.bool] = None,
        block_public_access: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess] = None,
        bucket_key_enabled: typing.Optional[builtins.bool] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        cors: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.CorsRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        encryption: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        enforce_ssl: typing.Optional[builtins.bool] = None,
        event_bridge_enabled: typing.Optional[builtins.bool] = None,
        intelligent_tiering_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        inventories: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.Inventory, typing.Dict[builtins.str, typing.Any]]]] = None,
        lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        metrics: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketMetrics, typing.Dict[builtins.str, typing.Any]]]] = None,
        minimum_tls_version: typing.Optional[jsii.Number] = None,
        notifications_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        notifications_skip_destination_validation: typing.Optional[builtins.bool] = None,
        object_lock_default_retention: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention] = None,
        object_lock_enabled: typing.Optional[builtins.bool] = None,
        object_ownership: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership] = None,
        public_read_access: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        replication_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        replication_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.ReplicationRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        server_access_logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        server_access_logs_prefix: typing.Optional[builtins.str] = None,
        target_object_key_format: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat] = None,
        transfer_acceleration: typing.Optional[builtins.bool] = None,
        transition_default_minimum_object_size: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize] = None,
        versioned: typing.Optional[builtins.bool] = None,
        website_error_document: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
        website_redirect: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.RedirectTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        website_routing_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.RoutingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Constructs a new CrowdStrikeBucket.

        :param scope: The scope in which this construct is defined.
        :param id: The scoped construct ID.
        :param create_kms_key: Whether to create a KMS key for the bucket. Default: - false
        :param crowd_strike_external_id_parameter_arn: The ARN of the SSM parameter containing the CrowdStrike external ID. Required unless the role principal is provided directly in the roleProps.
        :param crowd_strike_role_arn: The CrowdStrike role ARN. Required unless the role principal is provided directly in the roleProps.
        :param key_props: Properties for the KMS key. Default: - removalPolicy: RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE, enableKeyRotation: false, multiRegion: true, description: ``KMS Key for CrowdStrike ingestion bucket ${this.bucketName}``,
        :param logging_bucket_source_name: The name of the S3 bucket that will be sending S3 access logs to this bucket. This is used to configure the bucket policy to allow logging from that bucket. Default: - none
        :param org_id: The organization ID. If provided, the bucket will allow write access to all accounts in the organization. If there is a KMS key, it will also allow encrypt/decrypt access to the organization. Default: - none
        :param queue_props: Properties for the SQS queue. Default: - enforceSSL: true, deadLetterQueue: { maxReceiveCount: 5, queue: new sqs.Queue(this, 'DLQ', { queueName: ``${this.bucketName}-dlq``, enforceSSL: true, }), },
        :param role_props: Properties for the IAM role. If you provide this, you must provide the roleProps.assumedBy property, and you don't need to provide the crowdStrikeRoleParameterArn and crowdStrikeExternalIdParameterArn. Default: - none except for the assumedBy property which is set to a CrowdStrike principal.
        :param access_control: Specifies a canned ACL that grants predefined permissions to the bucket. Default: BucketAccessControl.PRIVATE
        :param auto_delete_objects: Whether all objects should be automatically deleted when the bucket is removed from the stack or when the stack is deleted. Requires the ``removalPolicy`` to be set to ``RemovalPolicy.DESTROY``. **Warning** if you have deployed a bucket with ``autoDeleteObjects: true``, switching this to ``false`` in a CDK version *before* ``1.126.0`` will lead to all objects in the bucket being deleted. Be sure to update your bucket resources by deploying with CDK version ``1.126.0`` or later **before** switching this value to ``false``. Setting ``autoDeleteObjects`` to true on a bucket will add ``s3:PutBucketPolicy`` to the bucket policy. This is because during bucket deletion, the custom resource provider needs to update the bucket policy by adding a deny policy for ``s3:PutObject`` to prevent race conditions with external bucket writers. Default: false
        :param block_public_access: The block public access configuration of this bucket. Default: - CloudFormation defaults will apply. New buckets and objects don't allow public access, but users can modify bucket policies or object permissions to allow public access
        :param bucket_key_enabled: Whether Amazon S3 should use its own intermediary key to generate data keys. Only relevant when using KMS for encryption. - If not enabled, every object GET and PUT will cause an API call to KMS (with the attendant cost implications of that). - If enabled, S3 will use its own time-limited key instead. Only relevant, when Encryption is not set to ``BucketEncryption.UNENCRYPTED``. Default: - false
        :param bucket_name: Physical name of this bucket. Default: - Assigned by CloudFormation (recommended).
        :param cors: The CORS configuration of this bucket. Default: - No CORS configuration.
        :param encryption: The kind of server-side encryption to apply to this bucket. If you choose KMS, you can specify a KMS key via ``encryptionKey``. If encryption key is not specified, a key will automatically be created. Default: - ``KMS`` if ``encryptionKey`` is specified, or ``S3_MANAGED`` otherwise.
        :param encryption_key: External KMS key to use for bucket encryption. The ``encryption`` property must be either not specified or set to ``KMS`` or ``DSSE``. An error will be emitted if ``encryption`` is set to ``UNENCRYPTED`` or ``S3_MANAGED``. Default: - If ``encryption`` is set to ``KMS`` and this property is undefined, a new KMS key will be created and associated with this bucket.
        :param enforce_ssl: Enforces SSL for requests. S3.5 of the AWS Foundational Security Best Practices Regarding S3. Default: false
        :param event_bridge_enabled: Whether this bucket should send notifications to Amazon EventBridge or not. Default: false
        :param intelligent_tiering_configurations: Intelligent Tiering Configurations. Default: No Intelligent Tiiering Configurations.
        :param inventories: The inventory configuration of the bucket. Default: - No inventory configuration
        :param lifecycle_rules: Rules that define how Amazon S3 manages objects during their lifetime. Default: - No lifecycle rules.
        :param metrics: The metrics configuration of this bucket. Default: - No metrics configuration.
        :param minimum_tls_version: Enforces minimum TLS version for requests. Requires ``enforceSSL`` to be enabled. Default: No minimum TLS version is enforced.
        :param notifications_handler_role: The role to be used by the notifications handler. Default: - a new role will be created.
        :param notifications_skip_destination_validation: Skips notification validation of Amazon SQS, Amazon SNS, and Lambda destinations. Default: false
        :param object_lock_default_retention: The default retention mode and rules for S3 Object Lock. Default retention can be configured after a bucket is created if the bucket already has object lock enabled. Enabling object lock for existing buckets is not supported. Default: no default retention period
        :param object_lock_enabled: Enable object lock on the bucket. Enabling object lock for existing buckets is not supported. Object lock must be enabled when the bucket is created. Default: false, unless objectLockDefaultRetention is set (then, true)
        :param object_ownership: The objectOwnership of the bucket. Default: - No ObjectOwnership configuration. By default, Amazon S3 sets Object Ownership to ``Bucket owner enforced``. This means ACLs are disabled and the bucket owner will own every object.
        :param public_read_access: Grants public read access to all objects in the bucket. Similar to calling ``bucket.grantPublicAccess()`` Default: false
        :param removal_policy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
        :param replication_role: The role to be used by the replication. When setting this property, you must also set ``replicationRules``. Default: - a new role will be created.
        :param replication_rules: A container for one or more replication rules. Default: - No replication
        :param server_access_logs_bucket: Destination bucket for the server access logs. Default: - If "serverAccessLogsPrefix" undefined - access logs disabled, otherwise - log to current bucket.
        :param server_access_logs_prefix: Optional log file prefix to use for the bucket's access logs. If defined without "serverAccessLogsBucket", enables access logs to current bucket with this prefix. Default: - No log file prefix
        :param target_object_key_format: Optional key format for log objects. Default: - the default key format is: [DestinationPrefix][YYYY]-[MM]-[DD]-[hh]-[mm]-[ss]-[UniqueString]
        :param transfer_acceleration: Whether this bucket should have transfer acceleration turned on or not. Default: false
        :param transition_default_minimum_object_size: Indicates which default minimum object size behavior is applied to the lifecycle configuration. To customize the minimum object size for any transition you can add a filter that specifies a custom ``objectSizeGreaterThan`` or ``objectSizeLessThan`` for ``lifecycleRules`` property. Custom filters always take precedence over the default transition behavior. Default: - TransitionDefaultMinimumObjectSize.VARIES_BY_STORAGE_CLASS before September 2024, otherwise TransitionDefaultMinimumObjectSize.ALL_STORAGE_CLASSES_128_K.
        :param versioned: Whether this bucket should have versioning turned on or not. Default: false (unless object lock is enabled, then true)
        :param website_error_document: The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set. Default: - No error document.
        :param website_index_document: The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket. Default: - No index document.
        :param website_redirect: Specifies the redirect behavior of all requests to a website endpoint of a bucket. If you specify this property, you can't specify "websiteIndexDocument", "websiteErrorDocument" nor , "websiteRoutingRules". Default: - No redirection.
        :param website_routing_rules: Rules that define when a redirect is applied and the redirect behavior. Default: - No redirection rules.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57fa082c525840a81651d73c87d35379d43a6484ae9d3651a36d61b099ba30fa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CrowdStrikeBucketProps(
            create_kms_key=create_kms_key,
            crowd_strike_external_id_parameter_arn=crowd_strike_external_id_parameter_arn,
            crowd_strike_role_arn=crowd_strike_role_arn,
            key_props=key_props,
            logging_bucket_source_name=logging_bucket_source_name,
            org_id=org_id,
            queue_props=queue_props,
            role_props=role_props,
            access_control=access_control,
            auto_delete_objects=auto_delete_objects,
            block_public_access=block_public_access,
            bucket_key_enabled=bucket_key_enabled,
            bucket_name=bucket_name,
            cors=cors,
            encryption=encryption,
            encryption_key=encryption_key,
            enforce_ssl=enforce_ssl,
            event_bridge_enabled=event_bridge_enabled,
            intelligent_tiering_configurations=intelligent_tiering_configurations,
            inventories=inventories,
            lifecycle_rules=lifecycle_rules,
            metrics=metrics,
            minimum_tls_version=minimum_tls_version,
            notifications_handler_role=notifications_handler_role,
            notifications_skip_destination_validation=notifications_skip_destination_validation,
            object_lock_default_retention=object_lock_default_retention,
            object_lock_enabled=object_lock_enabled,
            object_ownership=object_ownership,
            public_read_access=public_read_access,
            removal_policy=removal_policy,
            replication_role=replication_role,
            replication_rules=replication_rules,
            server_access_logs_bucket=server_access_logs_bucket,
            server_access_logs_prefix=server_access_logs_prefix,
            target_object_key_format=target_object_key_format,
            transfer_acceleration=transfer_acceleration,
            transition_default_minimum_object_size=transition_default_minimum_object_size,
            versioned=versioned,
            website_error_document=website_error_document,
            website_index_document=website_index_document,
            website_redirect=website_redirect,
            website_routing_rules=website_routing_rules,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="queue")
    def queue(self) -> _aws_cdk_aws_sqs_ceddda9d.Queue:
        '''The SQS queue that receives notifications for new objects in the bucket.'''
        return typing.cast(_aws_cdk_aws_sqs_ceddda9d.Queue, jsii.get(self, "queue"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''The IAM role that CrowdStrike will assume to access the data in the bucket.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''The KMS key used for encrypting data in the bucket, if created. This will be undefined if createKmsKey is false.

        Note that the bucket will still be created with S3-managed encryption
        even if this is provided. The key is used by the service writing to the bucket.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], jsii.get(self, "key"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-crowdstrike-ingestion.CrowdStrikeBucketProps",
    jsii_struct_bases=[_aws_cdk_aws_s3_ceddda9d.BucketProps],
    name_mapping={
        "access_control": "accessControl",
        "auto_delete_objects": "autoDeleteObjects",
        "block_public_access": "blockPublicAccess",
        "bucket_key_enabled": "bucketKeyEnabled",
        "bucket_name": "bucketName",
        "cors": "cors",
        "encryption": "encryption",
        "encryption_key": "encryptionKey",
        "enforce_ssl": "enforceSSL",
        "event_bridge_enabled": "eventBridgeEnabled",
        "intelligent_tiering_configurations": "intelligentTieringConfigurations",
        "inventories": "inventories",
        "lifecycle_rules": "lifecycleRules",
        "metrics": "metrics",
        "minimum_tls_version": "minimumTLSVersion",
        "notifications_handler_role": "notificationsHandlerRole",
        "notifications_skip_destination_validation": "notificationsSkipDestinationValidation",
        "object_lock_default_retention": "objectLockDefaultRetention",
        "object_lock_enabled": "objectLockEnabled",
        "object_ownership": "objectOwnership",
        "public_read_access": "publicReadAccess",
        "removal_policy": "removalPolicy",
        "replication_role": "replicationRole",
        "replication_rules": "replicationRules",
        "server_access_logs_bucket": "serverAccessLogsBucket",
        "server_access_logs_prefix": "serverAccessLogsPrefix",
        "target_object_key_format": "targetObjectKeyFormat",
        "transfer_acceleration": "transferAcceleration",
        "transition_default_minimum_object_size": "transitionDefaultMinimumObjectSize",
        "versioned": "versioned",
        "website_error_document": "websiteErrorDocument",
        "website_index_document": "websiteIndexDocument",
        "website_redirect": "websiteRedirect",
        "website_routing_rules": "websiteRoutingRules",
        "create_kms_key": "createKmsKey",
        "crowd_strike_external_id_parameter_arn": "crowdStrikeExternalIdParameterArn",
        "crowd_strike_role_arn": "crowdStrikeRoleArn",
        "key_props": "keyProps",
        "logging_bucket_source_name": "loggingBucketSourceName",
        "org_id": "orgId",
        "queue_props": "queueProps",
        "role_props": "roleProps",
    },
)
class CrowdStrikeBucketProps(_aws_cdk_aws_s3_ceddda9d.BucketProps):
    def __init__(
        self,
        *,
        access_control: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl] = None,
        auto_delete_objects: typing.Optional[builtins.bool] = None,
        block_public_access: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess] = None,
        bucket_key_enabled: typing.Optional[builtins.bool] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        cors: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.CorsRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        encryption: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        enforce_ssl: typing.Optional[builtins.bool] = None,
        event_bridge_enabled: typing.Optional[builtins.bool] = None,
        intelligent_tiering_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        inventories: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.Inventory, typing.Dict[builtins.str, typing.Any]]]] = None,
        lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        metrics: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketMetrics, typing.Dict[builtins.str, typing.Any]]]] = None,
        minimum_tls_version: typing.Optional[jsii.Number] = None,
        notifications_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        notifications_skip_destination_validation: typing.Optional[builtins.bool] = None,
        object_lock_default_retention: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention] = None,
        object_lock_enabled: typing.Optional[builtins.bool] = None,
        object_ownership: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership] = None,
        public_read_access: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        replication_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        replication_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.ReplicationRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        server_access_logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        server_access_logs_prefix: typing.Optional[builtins.str] = None,
        target_object_key_format: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat] = None,
        transfer_acceleration: typing.Optional[builtins.bool] = None,
        transition_default_minimum_object_size: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize] = None,
        versioned: typing.Optional[builtins.bool] = None,
        website_error_document: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
        website_redirect: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.RedirectTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        website_routing_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.RoutingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        create_kms_key: typing.Optional[builtins.bool] = None,
        crowd_strike_external_id_parameter_arn: typing.Optional[builtins.str] = None,
        crowd_strike_role_arn: typing.Optional[builtins.str] = None,
        key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        logging_bucket_source_name: typing.Optional[builtins.str] = None,
        org_id: typing.Optional[builtins.str] = None,
        queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
        role_props: typing.Optional[typing.Union[_aws_cdk_aws_iam_ceddda9d.RoleProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties for the CrowdStrikeBucket construct.

        :param access_control: Specifies a canned ACL that grants predefined permissions to the bucket. Default: BucketAccessControl.PRIVATE
        :param auto_delete_objects: Whether all objects should be automatically deleted when the bucket is removed from the stack or when the stack is deleted. Requires the ``removalPolicy`` to be set to ``RemovalPolicy.DESTROY``. **Warning** if you have deployed a bucket with ``autoDeleteObjects: true``, switching this to ``false`` in a CDK version *before* ``1.126.0`` will lead to all objects in the bucket being deleted. Be sure to update your bucket resources by deploying with CDK version ``1.126.0`` or later **before** switching this value to ``false``. Setting ``autoDeleteObjects`` to true on a bucket will add ``s3:PutBucketPolicy`` to the bucket policy. This is because during bucket deletion, the custom resource provider needs to update the bucket policy by adding a deny policy for ``s3:PutObject`` to prevent race conditions with external bucket writers. Default: false
        :param block_public_access: The block public access configuration of this bucket. Default: - CloudFormation defaults will apply. New buckets and objects don't allow public access, but users can modify bucket policies or object permissions to allow public access
        :param bucket_key_enabled: Whether Amazon S3 should use its own intermediary key to generate data keys. Only relevant when using KMS for encryption. - If not enabled, every object GET and PUT will cause an API call to KMS (with the attendant cost implications of that). - If enabled, S3 will use its own time-limited key instead. Only relevant, when Encryption is not set to ``BucketEncryption.UNENCRYPTED``. Default: - false
        :param bucket_name: Physical name of this bucket. Default: - Assigned by CloudFormation (recommended).
        :param cors: The CORS configuration of this bucket. Default: - No CORS configuration.
        :param encryption: The kind of server-side encryption to apply to this bucket. If you choose KMS, you can specify a KMS key via ``encryptionKey``. If encryption key is not specified, a key will automatically be created. Default: - ``KMS`` if ``encryptionKey`` is specified, or ``S3_MANAGED`` otherwise.
        :param encryption_key: External KMS key to use for bucket encryption. The ``encryption`` property must be either not specified or set to ``KMS`` or ``DSSE``. An error will be emitted if ``encryption`` is set to ``UNENCRYPTED`` or ``S3_MANAGED``. Default: - If ``encryption`` is set to ``KMS`` and this property is undefined, a new KMS key will be created and associated with this bucket.
        :param enforce_ssl: Enforces SSL for requests. S3.5 of the AWS Foundational Security Best Practices Regarding S3. Default: false
        :param event_bridge_enabled: Whether this bucket should send notifications to Amazon EventBridge or not. Default: false
        :param intelligent_tiering_configurations: Intelligent Tiering Configurations. Default: No Intelligent Tiiering Configurations.
        :param inventories: The inventory configuration of the bucket. Default: - No inventory configuration
        :param lifecycle_rules: Rules that define how Amazon S3 manages objects during their lifetime. Default: - No lifecycle rules.
        :param metrics: The metrics configuration of this bucket. Default: - No metrics configuration.
        :param minimum_tls_version: Enforces minimum TLS version for requests. Requires ``enforceSSL`` to be enabled. Default: No minimum TLS version is enforced.
        :param notifications_handler_role: The role to be used by the notifications handler. Default: - a new role will be created.
        :param notifications_skip_destination_validation: Skips notification validation of Amazon SQS, Amazon SNS, and Lambda destinations. Default: false
        :param object_lock_default_retention: The default retention mode and rules for S3 Object Lock. Default retention can be configured after a bucket is created if the bucket already has object lock enabled. Enabling object lock for existing buckets is not supported. Default: no default retention period
        :param object_lock_enabled: Enable object lock on the bucket. Enabling object lock for existing buckets is not supported. Object lock must be enabled when the bucket is created. Default: false, unless objectLockDefaultRetention is set (then, true)
        :param object_ownership: The objectOwnership of the bucket. Default: - No ObjectOwnership configuration. By default, Amazon S3 sets Object Ownership to ``Bucket owner enforced``. This means ACLs are disabled and the bucket owner will own every object.
        :param public_read_access: Grants public read access to all objects in the bucket. Similar to calling ``bucket.grantPublicAccess()`` Default: false
        :param removal_policy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
        :param replication_role: The role to be used by the replication. When setting this property, you must also set ``replicationRules``. Default: - a new role will be created.
        :param replication_rules: A container for one or more replication rules. Default: - No replication
        :param server_access_logs_bucket: Destination bucket for the server access logs. Default: - If "serverAccessLogsPrefix" undefined - access logs disabled, otherwise - log to current bucket.
        :param server_access_logs_prefix: Optional log file prefix to use for the bucket's access logs. If defined without "serverAccessLogsBucket", enables access logs to current bucket with this prefix. Default: - No log file prefix
        :param target_object_key_format: Optional key format for log objects. Default: - the default key format is: [DestinationPrefix][YYYY]-[MM]-[DD]-[hh]-[mm]-[ss]-[UniqueString]
        :param transfer_acceleration: Whether this bucket should have transfer acceleration turned on or not. Default: false
        :param transition_default_minimum_object_size: Indicates which default minimum object size behavior is applied to the lifecycle configuration. To customize the minimum object size for any transition you can add a filter that specifies a custom ``objectSizeGreaterThan`` or ``objectSizeLessThan`` for ``lifecycleRules`` property. Custom filters always take precedence over the default transition behavior. Default: - TransitionDefaultMinimumObjectSize.VARIES_BY_STORAGE_CLASS before September 2024, otherwise TransitionDefaultMinimumObjectSize.ALL_STORAGE_CLASSES_128_K.
        :param versioned: Whether this bucket should have versioning turned on or not. Default: false (unless object lock is enabled, then true)
        :param website_error_document: The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set. Default: - No error document.
        :param website_index_document: The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket. Default: - No index document.
        :param website_redirect: Specifies the redirect behavior of all requests to a website endpoint of a bucket. If you specify this property, you can't specify "websiteIndexDocument", "websiteErrorDocument" nor , "websiteRoutingRules". Default: - No redirection.
        :param website_routing_rules: Rules that define when a redirect is applied and the redirect behavior. Default: - No redirection rules.
        :param create_kms_key: Whether to create a KMS key for the bucket. Default: - false
        :param crowd_strike_external_id_parameter_arn: The ARN of the SSM parameter containing the CrowdStrike external ID. Required unless the role principal is provided directly in the roleProps.
        :param crowd_strike_role_arn: The CrowdStrike role ARN. Required unless the role principal is provided directly in the roleProps.
        :param key_props: Properties for the KMS key. Default: - removalPolicy: RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE, enableKeyRotation: false, multiRegion: true, description: ``KMS Key for CrowdStrike ingestion bucket ${this.bucketName}``,
        :param logging_bucket_source_name: The name of the S3 bucket that will be sending S3 access logs to this bucket. This is used to configure the bucket policy to allow logging from that bucket. Default: - none
        :param org_id: The organization ID. If provided, the bucket will allow write access to all accounts in the organization. If there is a KMS key, it will also allow encrypt/decrypt access to the organization. Default: - none
        :param queue_props: Properties for the SQS queue. Default: - enforceSSL: true, deadLetterQueue: { maxReceiveCount: 5, queue: new sqs.Queue(this, 'DLQ', { queueName: ``${this.bucketName}-dlq``, enforceSSL: true, }), },
        :param role_props: Properties for the IAM role. If you provide this, you must provide the roleProps.assumedBy property, and you don't need to provide the crowdStrikeRoleParameterArn and crowdStrikeExternalIdParameterArn. Default: - none except for the assumedBy property which is set to a CrowdStrike principal.
        '''
        if isinstance(website_redirect, dict):
            website_redirect = _aws_cdk_aws_s3_ceddda9d.RedirectTarget(**website_redirect)
        if isinstance(key_props, dict):
            key_props = _aws_cdk_aws_kms_ceddda9d.KeyProps(**key_props)
        if isinstance(queue_props, dict):
            queue_props = _aws_cdk_aws_sqs_ceddda9d.QueueProps(**queue_props)
        if isinstance(role_props, dict):
            role_props = _aws_cdk_aws_iam_ceddda9d.RoleProps(**role_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba8dd082ced2cc40959ac629ef460a08c4a721d24aa0a10d535ddc86300a10d4)
            check_type(argname="argument access_control", value=access_control, expected_type=type_hints["access_control"])
            check_type(argname="argument auto_delete_objects", value=auto_delete_objects, expected_type=type_hints["auto_delete_objects"])
            check_type(argname="argument block_public_access", value=block_public_access, expected_type=type_hints["block_public_access"])
            check_type(argname="argument bucket_key_enabled", value=bucket_key_enabled, expected_type=type_hints["bucket_key_enabled"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument cors", value=cors, expected_type=type_hints["cors"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument enforce_ssl", value=enforce_ssl, expected_type=type_hints["enforce_ssl"])
            check_type(argname="argument event_bridge_enabled", value=event_bridge_enabled, expected_type=type_hints["event_bridge_enabled"])
            check_type(argname="argument intelligent_tiering_configurations", value=intelligent_tiering_configurations, expected_type=type_hints["intelligent_tiering_configurations"])
            check_type(argname="argument inventories", value=inventories, expected_type=type_hints["inventories"])
            check_type(argname="argument lifecycle_rules", value=lifecycle_rules, expected_type=type_hints["lifecycle_rules"])
            check_type(argname="argument metrics", value=metrics, expected_type=type_hints["metrics"])
            check_type(argname="argument minimum_tls_version", value=minimum_tls_version, expected_type=type_hints["minimum_tls_version"])
            check_type(argname="argument notifications_handler_role", value=notifications_handler_role, expected_type=type_hints["notifications_handler_role"])
            check_type(argname="argument notifications_skip_destination_validation", value=notifications_skip_destination_validation, expected_type=type_hints["notifications_skip_destination_validation"])
            check_type(argname="argument object_lock_default_retention", value=object_lock_default_retention, expected_type=type_hints["object_lock_default_retention"])
            check_type(argname="argument object_lock_enabled", value=object_lock_enabled, expected_type=type_hints["object_lock_enabled"])
            check_type(argname="argument object_ownership", value=object_ownership, expected_type=type_hints["object_ownership"])
            check_type(argname="argument public_read_access", value=public_read_access, expected_type=type_hints["public_read_access"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument replication_role", value=replication_role, expected_type=type_hints["replication_role"])
            check_type(argname="argument replication_rules", value=replication_rules, expected_type=type_hints["replication_rules"])
            check_type(argname="argument server_access_logs_bucket", value=server_access_logs_bucket, expected_type=type_hints["server_access_logs_bucket"])
            check_type(argname="argument server_access_logs_prefix", value=server_access_logs_prefix, expected_type=type_hints["server_access_logs_prefix"])
            check_type(argname="argument target_object_key_format", value=target_object_key_format, expected_type=type_hints["target_object_key_format"])
            check_type(argname="argument transfer_acceleration", value=transfer_acceleration, expected_type=type_hints["transfer_acceleration"])
            check_type(argname="argument transition_default_minimum_object_size", value=transition_default_minimum_object_size, expected_type=type_hints["transition_default_minimum_object_size"])
            check_type(argname="argument versioned", value=versioned, expected_type=type_hints["versioned"])
            check_type(argname="argument website_error_document", value=website_error_document, expected_type=type_hints["website_error_document"])
            check_type(argname="argument website_index_document", value=website_index_document, expected_type=type_hints["website_index_document"])
            check_type(argname="argument website_redirect", value=website_redirect, expected_type=type_hints["website_redirect"])
            check_type(argname="argument website_routing_rules", value=website_routing_rules, expected_type=type_hints["website_routing_rules"])
            check_type(argname="argument create_kms_key", value=create_kms_key, expected_type=type_hints["create_kms_key"])
            check_type(argname="argument crowd_strike_external_id_parameter_arn", value=crowd_strike_external_id_parameter_arn, expected_type=type_hints["crowd_strike_external_id_parameter_arn"])
            check_type(argname="argument crowd_strike_role_arn", value=crowd_strike_role_arn, expected_type=type_hints["crowd_strike_role_arn"])
            check_type(argname="argument key_props", value=key_props, expected_type=type_hints["key_props"])
            check_type(argname="argument logging_bucket_source_name", value=logging_bucket_source_name, expected_type=type_hints["logging_bucket_source_name"])
            check_type(argname="argument org_id", value=org_id, expected_type=type_hints["org_id"])
            check_type(argname="argument queue_props", value=queue_props, expected_type=type_hints["queue_props"])
            check_type(argname="argument role_props", value=role_props, expected_type=type_hints["role_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_control is not None:
            self._values["access_control"] = access_control
        if auto_delete_objects is not None:
            self._values["auto_delete_objects"] = auto_delete_objects
        if block_public_access is not None:
            self._values["block_public_access"] = block_public_access
        if bucket_key_enabled is not None:
            self._values["bucket_key_enabled"] = bucket_key_enabled
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if cors is not None:
            self._values["cors"] = cors
        if encryption is not None:
            self._values["encryption"] = encryption
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if enforce_ssl is not None:
            self._values["enforce_ssl"] = enforce_ssl
        if event_bridge_enabled is not None:
            self._values["event_bridge_enabled"] = event_bridge_enabled
        if intelligent_tiering_configurations is not None:
            self._values["intelligent_tiering_configurations"] = intelligent_tiering_configurations
        if inventories is not None:
            self._values["inventories"] = inventories
        if lifecycle_rules is not None:
            self._values["lifecycle_rules"] = lifecycle_rules
        if metrics is not None:
            self._values["metrics"] = metrics
        if minimum_tls_version is not None:
            self._values["minimum_tls_version"] = minimum_tls_version
        if notifications_handler_role is not None:
            self._values["notifications_handler_role"] = notifications_handler_role
        if notifications_skip_destination_validation is not None:
            self._values["notifications_skip_destination_validation"] = notifications_skip_destination_validation
        if object_lock_default_retention is not None:
            self._values["object_lock_default_retention"] = object_lock_default_retention
        if object_lock_enabled is not None:
            self._values["object_lock_enabled"] = object_lock_enabled
        if object_ownership is not None:
            self._values["object_ownership"] = object_ownership
        if public_read_access is not None:
            self._values["public_read_access"] = public_read_access
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if replication_role is not None:
            self._values["replication_role"] = replication_role
        if replication_rules is not None:
            self._values["replication_rules"] = replication_rules
        if server_access_logs_bucket is not None:
            self._values["server_access_logs_bucket"] = server_access_logs_bucket
        if server_access_logs_prefix is not None:
            self._values["server_access_logs_prefix"] = server_access_logs_prefix
        if target_object_key_format is not None:
            self._values["target_object_key_format"] = target_object_key_format
        if transfer_acceleration is not None:
            self._values["transfer_acceleration"] = transfer_acceleration
        if transition_default_minimum_object_size is not None:
            self._values["transition_default_minimum_object_size"] = transition_default_minimum_object_size
        if versioned is not None:
            self._values["versioned"] = versioned
        if website_error_document is not None:
            self._values["website_error_document"] = website_error_document
        if website_index_document is not None:
            self._values["website_index_document"] = website_index_document
        if website_redirect is not None:
            self._values["website_redirect"] = website_redirect
        if website_routing_rules is not None:
            self._values["website_routing_rules"] = website_routing_rules
        if create_kms_key is not None:
            self._values["create_kms_key"] = create_kms_key
        if crowd_strike_external_id_parameter_arn is not None:
            self._values["crowd_strike_external_id_parameter_arn"] = crowd_strike_external_id_parameter_arn
        if crowd_strike_role_arn is not None:
            self._values["crowd_strike_role_arn"] = crowd_strike_role_arn
        if key_props is not None:
            self._values["key_props"] = key_props
        if logging_bucket_source_name is not None:
            self._values["logging_bucket_source_name"] = logging_bucket_source_name
        if org_id is not None:
            self._values["org_id"] = org_id
        if queue_props is not None:
            self._values["queue_props"] = queue_props
        if role_props is not None:
            self._values["role_props"] = role_props

    @builtins.property
    def access_control(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl]:
        '''Specifies a canned ACL that grants predefined permissions to the bucket.

        :default: BucketAccessControl.PRIVATE
        '''
        result = self._values.get("access_control")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl], result)

    @builtins.property
    def auto_delete_objects(self) -> typing.Optional[builtins.bool]:
        '''Whether all objects should be automatically deleted when the bucket is removed from the stack or when the stack is deleted.

        Requires the ``removalPolicy`` to be set to ``RemovalPolicy.DESTROY``.

        **Warning** if you have deployed a bucket with ``autoDeleteObjects: true``,
        switching this to ``false`` in a CDK version *before* ``1.126.0`` will lead to
        all objects in the bucket being deleted. Be sure to update your bucket resources
        by deploying with CDK version ``1.126.0`` or later **before** switching this value to ``false``.

        Setting ``autoDeleteObjects`` to true on a bucket will add ``s3:PutBucketPolicy`` to the
        bucket policy. This is because during bucket deletion, the custom resource provider
        needs to update the bucket policy by adding a deny policy for ``s3:PutObject`` to
        prevent race conditions with external bucket writers.

        :default: false
        '''
        result = self._values.get("auto_delete_objects")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def block_public_access(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess]:
        '''The block public access configuration of this bucket.

        :default: - CloudFormation defaults will apply. New buckets and objects don't allow public access, but users can modify bucket policies or object permissions to allow public access

        :see: https://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-block-public-access.html
        '''
        result = self._values.get("block_public_access")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess], result)

    @builtins.property
    def bucket_key_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether Amazon S3 should use its own intermediary key to generate data keys.

        Only relevant when using KMS for encryption.

        - If not enabled, every object GET and PUT will cause an API call to KMS (with the
          attendant cost implications of that).
        - If enabled, S3 will use its own time-limited key instead.

        Only relevant, when Encryption is not set to ``BucketEncryption.UNENCRYPTED``.

        :default: - false
        '''
        result = self._values.get("bucket_key_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Physical name of this bucket.

        :default: - Assigned by CloudFormation (recommended).
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cors(self) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.CorsRule]]:
        '''The CORS configuration of this bucket.

        :default: - No CORS configuration.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-cors.html
        '''
        result = self._values.get("cors")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.CorsRule]], result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption]:
        '''The kind of server-side encryption to apply to this bucket.

        If you choose KMS, you can specify a KMS key via ``encryptionKey``. If
        encryption key is not specified, a key will automatically be created.

        :default: - ``KMS`` if ``encryptionKey`` is specified, or ``S3_MANAGED`` otherwise.
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''External KMS key to use for bucket encryption.

        The ``encryption`` property must be either not specified or set to ``KMS`` or ``DSSE``.
        An error will be emitted if ``encryption`` is set to ``UNENCRYPTED`` or ``S3_MANAGED``.

        :default:

        - If ``encryption`` is set to ``KMS`` and this property is undefined,
        a new KMS key will be created and associated with this bucket.
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def enforce_ssl(self) -> typing.Optional[builtins.bool]:
        '''Enforces SSL for requests.

        S3.5 of the AWS Foundational Security Best Practices Regarding S3.

        :default: false

        :see: https://docs.aws.amazon.com/config/latest/developerguide/s3-bucket-ssl-requests-only.html
        '''
        result = self._values.get("enforce_ssl")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def event_bridge_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether this bucket should send notifications to Amazon EventBridge or not.

        :default: false
        '''
        result = self._values.get("event_bridge_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def intelligent_tiering_configurations(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration]]:
        '''Intelligent Tiering Configurations.

        :default: No Intelligent Tiiering Configurations.

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering.html
        '''
        result = self._values.get("intelligent_tiering_configurations")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration]], result)

    @builtins.property
    def inventories(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.Inventory]]:
        '''The inventory configuration of the bucket.

        :default: - No inventory configuration

        :see: https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-inventory.html
        '''
        result = self._values.get("inventories")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.Inventory]], result)

    @builtins.property
    def lifecycle_rules(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.LifecycleRule]]:
        '''Rules that define how Amazon S3 manages objects during their lifetime.

        :default: - No lifecycle rules.
        '''
        result = self._values.get("lifecycle_rules")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.LifecycleRule]], result)

    @builtins.property
    def metrics(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.BucketMetrics]]:
        '''The metrics configuration of this bucket.

        :default: - No metrics configuration.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-metricsconfiguration.html
        '''
        result = self._values.get("metrics")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.BucketMetrics]], result)

    @builtins.property
    def minimum_tls_version(self) -> typing.Optional[jsii.Number]:
        '''Enforces minimum TLS version for requests.

        Requires ``enforceSSL`` to be enabled.

        :default: No minimum TLS version is enforced.

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/amazon-s3-policy-keys.html#example-object-tls-version
        '''
        result = self._values.get("minimum_tls_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def notifications_handler_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The role to be used by the notifications handler.

        :default: - a new role will be created.
        '''
        result = self._values.get("notifications_handler_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def notifications_skip_destination_validation(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''Skips notification validation of Amazon SQS, Amazon SNS, and Lambda destinations.

        :default: false
        '''
        result = self._values.get("notifications_skip_destination_validation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def object_lock_default_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention]:
        '''The default retention mode and rules for S3 Object Lock.

        Default retention can be configured after a bucket is created if the bucket already
        has object lock enabled. Enabling object lock for existing buckets is not supported.

        :default: no default retention period

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html#object-lock-bucket-config-enable
        '''
        result = self._values.get("object_lock_default_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention], result)

    @builtins.property
    def object_lock_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable object lock on the bucket.

        Enabling object lock for existing buckets is not supported. Object lock must be
        enabled when the bucket is created.

        :default: false, unless objectLockDefaultRetention is set (then, true)

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html#object-lock-bucket-config-enable
        '''
        result = self._values.get("object_lock_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def object_ownership(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership]:
        '''The objectOwnership of the bucket.

        :default:

        - No ObjectOwnership configuration. By default, Amazon S3 sets Object Ownership to ``Bucket owner enforced``.
        This means ACLs are disabled and the bucket owner will own every object.

        :see: https://docs.aws.amazon.com/AmazonS3/latest/dev/about-object-ownership.html
        '''
        result = self._values.get("object_ownership")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership], result)

    @builtins.property
    def public_read_access(self) -> typing.Optional[builtins.bool]:
        '''Grants public read access to all objects in the bucket.

        Similar to calling ``bucket.grantPublicAccess()``

        :default: false
        '''
        result = self._values.get("public_read_access")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Policy to apply when the bucket is removed from this stack.

        :default: - The bucket will be orphaned.
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def replication_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The role to be used by the replication.

        When setting this property, you must also set ``replicationRules``.

        :default: - a new role will be created.
        '''
        result = self._values.get("replication_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def replication_rules(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.ReplicationRule]]:
        '''A container for one or more replication rules.

        :default: - No replication
        '''
        result = self._values.get("replication_rules")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.ReplicationRule]], result)

    @builtins.property
    def server_access_logs_bucket(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''Destination bucket for the server access logs.

        :default: - If "serverAccessLogsPrefix" undefined - access logs disabled, otherwise - log to current bucket.
        '''
        result = self._values.get("server_access_logs_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def server_access_logs_prefix(self) -> typing.Optional[builtins.str]:
        '''Optional log file prefix to use for the bucket's access logs.

        If defined without "serverAccessLogsBucket", enables access logs to current bucket with this prefix.

        :default: - No log file prefix
        '''
        result = self._values.get("server_access_logs_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_object_key_format(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat]:
        '''Optional key format for log objects.

        :default: - the default key format is: [DestinationPrefix][YYYY]-[MM]-[DD]-[hh]-[mm]-[ss]-[UniqueString]
        '''
        result = self._values.get("target_object_key_format")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat], result)

    @builtins.property
    def transfer_acceleration(self) -> typing.Optional[builtins.bool]:
        '''Whether this bucket should have transfer acceleration turned on or not.

        :default: false
        '''
        result = self._values.get("transfer_acceleration")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def transition_default_minimum_object_size(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize]:
        '''Indicates which default minimum object size behavior is applied to the lifecycle configuration.

        To customize the minimum object size for any transition you can add a filter that specifies a custom
        ``objectSizeGreaterThan`` or ``objectSizeLessThan`` for ``lifecycleRules`` property. Custom filters always
        take precedence over the default transition behavior.

        :default:

        - TransitionDefaultMinimumObjectSize.VARIES_BY_STORAGE_CLASS before September 2024,
        otherwise TransitionDefaultMinimumObjectSize.ALL_STORAGE_CLASSES_128_K.
        '''
        result = self._values.get("transition_default_minimum_object_size")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize], result)

    @builtins.property
    def versioned(self) -> typing.Optional[builtins.bool]:
        '''Whether this bucket should have versioning turned on or not.

        :default: false (unless object lock is enabled, then true)
        '''
        result = self._values.get("versioned")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def website_error_document(self) -> typing.Optional[builtins.str]:
        '''The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set.

        :default: - No error document.
        '''
        result = self._values.get("website_error_document")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def website_index_document(self) -> typing.Optional[builtins.str]:
        '''The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket.

        :default: - No index document.
        '''
        result = self._values.get("website_index_document")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def website_redirect(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.RedirectTarget]:
        '''Specifies the redirect behavior of all requests to a website endpoint of a bucket.

        If you specify this property, you can't specify "websiteIndexDocument", "websiteErrorDocument" nor , "websiteRoutingRules".

        :default: - No redirection.
        '''
        result = self._values.get("website_redirect")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.RedirectTarget], result)

    @builtins.property
    def website_routing_rules(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.RoutingRule]]:
        '''Rules that define when a redirect is applied and the redirect behavior.

        :default: - No redirection rules.
        '''
        result = self._values.get("website_routing_rules")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.RoutingRule]], result)

    @builtins.property
    def create_kms_key(self) -> typing.Optional[builtins.bool]:
        '''Whether to create a KMS key for the bucket.

        :default: - false
        '''
        result = self._values.get("create_kms_key")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def crowd_strike_external_id_parameter_arn(self) -> typing.Optional[builtins.str]:
        '''The ARN of the SSM parameter containing the CrowdStrike external ID.

        Required unless the role principal is provided directly in the roleProps.
        '''
        result = self._values.get("crowd_strike_external_id_parameter_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def crowd_strike_role_arn(self) -> typing.Optional[builtins.str]:
        '''The CrowdStrike role ARN.

        Required unless the role principal is provided directly in the roleProps.
        '''
        result = self._values.get("crowd_strike_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_props(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps]:
        '''Properties for the KMS key.

        :default: - removalPolicy: RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE, enableKeyRotation: false, multiRegion: true, description: ``KMS Key for CrowdStrike ingestion bucket ${this.bucketName}``,
        '''
        result = self._values.get("key_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps], result)

    @builtins.property
    def logging_bucket_source_name(self) -> typing.Optional[builtins.str]:
        '''The name of the S3 bucket that will be sending S3 access logs to this bucket.

        This is used to configure the bucket policy to allow logging from that bucket.

        :default: - none
        '''
        result = self._values.get("logging_bucket_source_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def org_id(self) -> typing.Optional[builtins.str]:
        '''The organization ID.

        If provided, the bucket will allow write access to all accounts in the organization.
        If there is a KMS key, it will also allow encrypt/decrypt access to the organization.

        :default: - none
        '''
        result = self._values.get("org_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queue_props(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps]:
        '''Properties for the SQS queue.

        :default: - enforceSSL: true, deadLetterQueue: { maxReceiveCount: 5, queue: new sqs.Queue(this, 'DLQ', { queueName: ``${this.bucketName}-dlq``, enforceSSL: true, }), },
        '''
        result = self._values.get("queue_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps], result)

    @builtins.property
    def role_props(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.RoleProps]:
        '''Properties for the IAM role.

        If you provide this, you must provide the roleProps.assumedBy property,
        and you don't need to provide the crowdStrikeRoleParameterArn and crowdStrikeExternalIdParameterArn.

        :default: - none except for the assumedBy property which is set to a CrowdStrike principal.
        '''
        result = self._values.get("role_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.RoleProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrowdStrikeBucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CrowdStrikeLogSubscription(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-crowdstrike-ingestion.CrowdStrikeLogSubscription",
):
    '''A construct that creates an CloudWatch log group filter subscription for CrowdStrike data ingestion, along with an IAM role for access.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        log_destination_arn: builtins.str,
        log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
        filter_pattern: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''Constructs a new CrowdStrikeLogSubscription.

        :param scope: The scope in which this construct is defined.
        :param id: The scoped construct ID.
        :param log_destination_arn: The ARN of the log destination logical resource.
        :param log_group: The log group to create the subscription filter for.
        :param filter_pattern: The filter pattern for the subscription filter. Default: - '%.%' (matches all log events).
        :param role: The IAM role that CloudWatch Logs will assume to create the subscription. If not provided, a new role will be created with the necessary permissions. Default: - a new role will be created.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69c70df02e2f7a07800d539e1ec43a62e2faf6626470a228c646a3d29b45448a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CrowdStrikeLogSubscriptionProps(
            log_destination_arn=log_destination_arn,
            log_group=log_group,
            filter_pattern=filter_pattern,
            role=role,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The log group for which the subscription filter is created.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "logGroup"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM role that CloudWatch Logs will assume to create the subscription.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionFilter")
    def subscription_filter(self) -> _aws_cdk_aws_logs_ceddda9d.CfnSubscriptionFilter:
        '''The subscription filter for the log group.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.CfnSubscriptionFilter, jsii.get(self, "subscriptionFilter"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-crowdstrike-ingestion.CrowdStrikeLogSubscriptionProps",
    jsii_struct_bases=[],
    name_mapping={
        "log_destination_arn": "logDestinationArn",
        "log_group": "logGroup",
        "filter_pattern": "filterPattern",
        "role": "role",
    },
)
class CrowdStrikeLogSubscriptionProps:
    def __init__(
        self,
        *,
        log_destination_arn: builtins.str,
        log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
        filter_pattern: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''Properties for the CrowdStrikeLogSubscription construct.

        :param log_destination_arn: The ARN of the log destination logical resource.
        :param log_group: The log group to create the subscription filter for.
        :param filter_pattern: The filter pattern for the subscription filter. Default: - '%.%' (matches all log events).
        :param role: The IAM role that CloudWatch Logs will assume to create the subscription. If not provided, a new role will be created with the necessary permissions. Default: - a new role will be created.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a83df01d73ff5304159488e1dcb5db18936917c41e9f2ef07e4d1a8d25093ba)
            check_type(argname="argument log_destination_arn", value=log_destination_arn, expected_type=type_hints["log_destination_arn"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument filter_pattern", value=filter_pattern, expected_type=type_hints["filter_pattern"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "log_destination_arn": log_destination_arn,
            "log_group": log_group,
        }
        if filter_pattern is not None:
            self._values["filter_pattern"] = filter_pattern
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def log_destination_arn(self) -> builtins.str:
        '''The ARN of the log destination logical resource.'''
        result = self._values.get("log_destination_arn")
        assert result is not None, "Required property 'log_destination_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The log group to create the subscription filter for.'''
        result = self._values.get("log_group")
        assert result is not None, "Required property 'log_group' is missing"
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, result)

    @builtins.property
    def filter_pattern(self) -> typing.Optional[builtins.str]:
        '''The filter pattern for the subscription filter.

        :default: - '%.%' (matches all log events).
        '''
        result = self._values.get("filter_pattern")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role that CloudWatch Logs will assume to create the subscription.

        If not provided, a new role will be created with the necessary permissions.

        :default: - a new role will be created.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrowdStrikeLogSubscriptionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CrowdStrikeBucket",
    "CrowdStrikeBucketProps",
    "CrowdStrikeLogSubscription",
    "CrowdStrikeLogSubscriptionProps",
]

publication.publish()

def _typecheckingstub__57fa082c525840a81651d73c87d35379d43a6484ae9d3651a36d61b099ba30fa(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    create_kms_key: typing.Optional[builtins.bool] = None,
    crowd_strike_external_id_parameter_arn: typing.Optional[builtins.str] = None,
    crowd_strike_role_arn: typing.Optional[builtins.str] = None,
    key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    logging_bucket_source_name: typing.Optional[builtins.str] = None,
    org_id: typing.Optional[builtins.str] = None,
    queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    role_props: typing.Optional[typing.Union[_aws_cdk_aws_iam_ceddda9d.RoleProps, typing.Dict[builtins.str, typing.Any]]] = None,
    access_control: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl] = None,
    auto_delete_objects: typing.Optional[builtins.bool] = None,
    block_public_access: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess] = None,
    bucket_key_enabled: typing.Optional[builtins.bool] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    cors: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.CorsRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    encryption: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    enforce_ssl: typing.Optional[builtins.bool] = None,
    event_bridge_enabled: typing.Optional[builtins.bool] = None,
    intelligent_tiering_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    inventories: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.Inventory, typing.Dict[builtins.str, typing.Any]]]] = None,
    lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    metrics: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketMetrics, typing.Dict[builtins.str, typing.Any]]]] = None,
    minimum_tls_version: typing.Optional[jsii.Number] = None,
    notifications_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    notifications_skip_destination_validation: typing.Optional[builtins.bool] = None,
    object_lock_default_retention: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention] = None,
    object_lock_enabled: typing.Optional[builtins.bool] = None,
    object_ownership: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership] = None,
    public_read_access: typing.Optional[builtins.bool] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    replication_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    replication_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.ReplicationRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    server_access_logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    server_access_logs_prefix: typing.Optional[builtins.str] = None,
    target_object_key_format: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat] = None,
    transfer_acceleration: typing.Optional[builtins.bool] = None,
    transition_default_minimum_object_size: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize] = None,
    versioned: typing.Optional[builtins.bool] = None,
    website_error_document: typing.Optional[builtins.str] = None,
    website_index_document: typing.Optional[builtins.str] = None,
    website_redirect: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.RedirectTarget, typing.Dict[builtins.str, typing.Any]]] = None,
    website_routing_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.RoutingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba8dd082ced2cc40959ac629ef460a08c4a721d24aa0a10d535ddc86300a10d4(
    *,
    access_control: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl] = None,
    auto_delete_objects: typing.Optional[builtins.bool] = None,
    block_public_access: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess] = None,
    bucket_key_enabled: typing.Optional[builtins.bool] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    cors: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.CorsRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    encryption: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    enforce_ssl: typing.Optional[builtins.bool] = None,
    event_bridge_enabled: typing.Optional[builtins.bool] = None,
    intelligent_tiering_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    inventories: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.Inventory, typing.Dict[builtins.str, typing.Any]]]] = None,
    lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    metrics: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketMetrics, typing.Dict[builtins.str, typing.Any]]]] = None,
    minimum_tls_version: typing.Optional[jsii.Number] = None,
    notifications_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    notifications_skip_destination_validation: typing.Optional[builtins.bool] = None,
    object_lock_default_retention: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention] = None,
    object_lock_enabled: typing.Optional[builtins.bool] = None,
    object_ownership: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership] = None,
    public_read_access: typing.Optional[builtins.bool] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    replication_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    replication_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.ReplicationRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    server_access_logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    server_access_logs_prefix: typing.Optional[builtins.str] = None,
    target_object_key_format: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat] = None,
    transfer_acceleration: typing.Optional[builtins.bool] = None,
    transition_default_minimum_object_size: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize] = None,
    versioned: typing.Optional[builtins.bool] = None,
    website_error_document: typing.Optional[builtins.str] = None,
    website_index_document: typing.Optional[builtins.str] = None,
    website_redirect: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.RedirectTarget, typing.Dict[builtins.str, typing.Any]]] = None,
    website_routing_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.RoutingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    create_kms_key: typing.Optional[builtins.bool] = None,
    crowd_strike_external_id_parameter_arn: typing.Optional[builtins.str] = None,
    crowd_strike_role_arn: typing.Optional[builtins.str] = None,
    key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    logging_bucket_source_name: typing.Optional[builtins.str] = None,
    org_id: typing.Optional[builtins.str] = None,
    queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    role_props: typing.Optional[typing.Union[_aws_cdk_aws_iam_ceddda9d.RoleProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69c70df02e2f7a07800d539e1ec43a62e2faf6626470a228c646a3d29b45448a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    log_destination_arn: builtins.str,
    log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
    filter_pattern: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a83df01d73ff5304159488e1dcb5db18936917c41e9f2ef07e4d1a8d25093ba(
    *,
    log_destination_arn: builtins.str,
    log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
    filter_pattern: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass
