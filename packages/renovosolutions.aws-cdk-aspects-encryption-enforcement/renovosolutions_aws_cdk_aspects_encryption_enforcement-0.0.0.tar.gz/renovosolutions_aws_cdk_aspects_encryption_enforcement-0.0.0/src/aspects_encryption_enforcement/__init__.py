r'''
# cdk-aspects-library-encryption-enforcement

A CDK Aspects library that enforces encryption on AWS resources to help maintain security best practices in your infrastructure as code.

This library provides CDK Aspects that can be applied to your stacks to ensure that resources are properly encrypted. Currently, the library supports enforcing encryption on:

* Amazon EFS File Systems
* Amazon RDS Databases (both instances and clusters)

The aspects will add error annotations to any resources that don't have encryption enabled, preventing deployment unless encryption is properly configured or the resources are explicitly excluded.

## Features

* Enforces encryption on EFS File Systems
* Enforces encryption on RDS Database Instances and Clusters
* Allows excluding specific resources from enforcement by ID
* Works with both L1 (CfnResource) and L2 (higher-level) constructs
* Provides individual aspects for each resource family
* Offers a convenience method to add all aspects at once
* Prevents deployment of non-compliant resources unless explicitly excluded

## API Doc

See [API](API.md)

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Usage

The library provides two main aspects:

1. `EFSEncryptionEnforcementAspect` - Enforces encryption on EFS File Systems
2. `RDSEncryptionEnforcementAspect` - Enforces encryption on RDS Database Instances and Clusters

You can apply these aspects individually or use the `EncryptionEnforcement.addAllAspects()` convenience method to add all aspects at once.

## Examples

### TypeScript

```python
import { Stack, App, Aspects } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as efs from 'aws-cdk-lib/aws-efs';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import {
  EFSEncryptionEnforcementAspect,
  RDSEncryptionEnforcementAspect,
  EncryptionEnforcement
} from '@renovosolutions/cdk-aspects-library-encryption-enforcement';

class MyStack extends Stack {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    // Create a VPC for our resources
    const vpc = new ec2.Vpc(this, 'MyVpc');

    // Create an EFS FileSystem with encryption enabled (compliant)
    new efs.FileSystem(this, 'EncryptedFileSystem', {
      vpc,
      encrypted: true, // This is compliant
    });

    // Create an EFS FileSystem without encryption (non-compliant)
    // This will cause a deployment error unless excluded
    new efs.FileSystem(this, 'UnencryptedFileSystem', {
      vpc,
      encrypted: false, // This will be caught by the aspect
    });

    // Create an RDS instance with encryption enabled (compliant)
    new rds.DatabaseInstance(this, 'EncryptedInstance', {
      engine: rds.DatabaseInstanceEngine.MYSQL,
      vpc,
      storageEncrypted: true, // This is compliant
    });

    // Create an RDS instance without encryption (non-compliant)
    // This will cause a deployment error unless excluded
    new rds.DatabaseInstance(this, 'UnencryptedInstance', {
      engine: rds.DatabaseInstanceEngine.MYSQL,
      vpc,
      storageEncrypted: false, // This will be caught by the aspect
    });

    // Method 1: Apply aspects individually
    Aspects.of(this).add(new EFSEncryptionEnforcementAspect());
    Aspects.of(this).add(new RDSEncryptionEnforcementAspect());

    // Method 2: Apply all aspects at once with exclusions
    // EncryptionEnforcement.addAllAspects(this, {
    //   excludeResources: ['UnencryptedFileSystem', 'UnencryptedInstance'],
    // });
  }
}

const app = new App();
new MyStack(app, 'MyStack');
app.synth();
```

### Python

```python
from aws_cdk import (
    Stack,
    App,
    Aspects,
    aws_ec2 as ec2,
    aws_efs as efs,
    aws_rds as rds,
)
from constructs import Construct
from aspects_encryption_enforcement import (
    EFSEncryptionEnforcementAspect,
    RDSEncryptionEnforcementAspect,
    EncryptionEnforcement
)

class MyStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC for our resources
        vpc = ec2.Vpc(self, 'MyVpc')

        # Create an EFS FileSystem with encryption enabled (compliant)
        efs.FileSystem(self, 'EncryptedFileSystem',
            vpc=vpc,
            encrypted=True  # This is compliant
        )

        # Create an EFS FileSystem without encryption (non-compliant)
        # This will cause a deployment error unless excluded
        efs.FileSystem(self, 'UnencryptedFileSystem',
            vpc=vpc,
            encrypted=False  # This will be caught by the aspect
        )

        # Create an RDS instance with encryption enabled (compliant)
        rds.DatabaseInstance(self, 'EncryptedInstance',
            engine=rds.DatabaseInstanceEngine.MYSQL,
            vpc=vpc,
            storage_encrypted=True  # This is compliant
        )

        # Create an RDS instance without encryption (non-compliant)
        # This will cause a deployment error unless excluded
        rds.DatabaseInstance(self, 'UnencryptedInstance',
            engine=rds.DatabaseInstanceEngine.MYSQL,
            vpc=vpc,
            storage_encrypted=False  # This will be caught by the aspect
        )

        # Method 1: Apply aspects individually
        Aspects.of(self).add(EFSEncryptionEnforcementAspect())
        Aspects.of(self).add(RDSEncryptionEnforcementAspect())

        # Method 2: Apply all aspects at once with exclusions
        # EncryptionEnforcement.add_all_aspects(self,
        #     exclude_resources=['UnencryptedFileSystem', 'UnencryptedInstance']
        # )

app = App()
MyStack(app, 'MyStack')
app.synth()
```

### C Sharp

```csharp
using Amazon.CDK;
using EC2 = Amazon.CDK.AWS.EC2;
using EFS = Amazon.CDK.AWS.EFS;
using RDS = Amazon.CDK.AWS.RDS;
using Constructs;
using renovosolutions;

namespace MyApp
{
  public class MyStack : Stack
  {
    internal MyStack(Construct scope, string id, IStackProps props = null) : base(scope, id, props)
    {
      // Create a VPC for our resources
      var vpc = new EC2.Vpc(this, "MyVpc");

      // Create an EFS FileSystem with encryption enabled (compliant)
      new EFS.FileSystem(this, "EncryptedFileSystem", new EFS.FileSystemProps
      {
        Vpc = vpc,
        Encrypted = true // This is compliant
      });

      // Create an EFS FileSystem without encryption (non-compliant)
      // This will cause a deployment error unless excluded
      new EFS.FileSystem(this, "UnencryptedFileSystem", new EFS.FileSystemProps
      {
        Vpc = vpc,
        Encrypted = false // This will be caught by the aspect
      });

      // Create an RDS instance with encryption enabled (compliant)
      new RDS.DatabaseInstance(this, "EncryptedInstance", new RDS.DatabaseInstanceProps
      {
        Engine = RDS.DatabaseInstanceEngine.MYSQL,
        Vpc = vpc,
        StorageEncrypted = true // This is compliant
      });

      // Create an RDS instance without encryption (non-compliant)
      // This will cause a deployment error unless excluded
      new RDS.DatabaseInstance(this, "UnencryptedInstance", new RDS.DatabaseInstanceProps
      {
        Engine = RDS.DatabaseInstanceEngine.MYSQL,
        Vpc = vpc,
        StorageEncrypted = false // This will be caught by the aspect
      });

      // Method 1: Apply aspects individually
      Aspects.Of(this).Add(new EFSEncryptionEnforcementAspect());
      Aspects.Of(this).Add(new RDSEncryptionEnforcementAspect());

      // Method 2: Apply all aspects at once with exclusions
      // EncryptionEnforcement.AddAllAspects(this, new EncryptionEnforcementAspectProps
      // {
      //     ExcludeResources = new[] { "UnencryptedFileSystem", "UnencryptedInstance" }
      // });
    }
  }

    class Program
    {
        static void Main(string[] args)
        {
            var app = new App();
            new MyStack(app, "MyStack");
            app.Synth();
        }
    }
}
```

## Excluding Resources

If you have specific resources that should be exempt from encryption enforcement, you can exclude them by ID:

```python
// Exclude specific resources
Aspects.of(stack).add(new EFSEncryptionEnforcementAspect({
  excludeResources: ['MyFileSystem', 'MyOtherFileSystem'],
}));

// Or exclude resources from all aspects at once
EncryptionEnforcement.addAllAspects(stack, {
  excludeResources: ['MyFileSystem', 'MyDatabaseInstance'],
});
```

The `excludeResources` property accepts an array of resource IDs. You can use either the L1 (CfnResource) ID or the L2 (higher-level construct) ID.
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
import constructs as _constructs_77d1e7e8


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class EFSEncryptionEnforcementAspect(
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-encryption-enforcement.EFSEncryptionEnforcementAspect",
):
    '''An aspect that enforces encryption on all EFS FileSystems in the stack.'''

    def __init__(
        self,
        *,
        exclude_resources: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Constructs a new EncryptionEnforcementAspect.

        :param exclude_resources: The resources to exclude from enforcement. Use a resource's ID to exclude a specific resource. Supports both CfnResource and L2 construct IDs. Default: []
        '''
        props = EncryptionEnforcementAspectProps(exclude_resources=exclude_resources)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''Visits each construct in the stack and enforces encryption on EFS FileSystems.

        :param node: - The construct to visit.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19aeef40ce4bb911317e08c2b766f5ea7c1eb1f3729da90daa941c240c56c058)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))

    @builtins.property
    @jsii.member(jsii_name="excludeResources")
    def exclude_resources(self) -> typing.List[builtins.str]:
        '''The resources to exclude from enforcement.

        Use a resource's ID to exclude a specific resource.
        Supports both CfnResource and L2 construct IDs.

        :default: []
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludeResources"))


class EncryptionEnforcement(
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-encryption-enforcement.EncryptionEnforcement",
):
    '''An convenience class with a static function that adds all of the aspects in this module.

    It's only a class because jsii skips standalone functions.
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="addAllAspects")
    @builtins.classmethod
    def add_all_aspects(
        cls,
        scope: _constructs_77d1e7e8.IConstruct,
        *,
        exclude_resources: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Adds all encryption enforcement aspects to the given scope.

        This is a convenience method to add all aspects in this module at once.
        It can be used in the ``main`` function of your CDK app or in a stack constructor.

        :param scope: - The scope to add the aspects to.
        :param exclude_resources: The resources to exclude from enforcement. Use a resource's ID to exclude a specific resource. Supports both CfnResource and L2 construct IDs. Default: []

        :return: void
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e738479d84cc73bc794d6554ccf1576444abd88b913e87f265638a2f4155b4d6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        props = EncryptionEnforcementAspectProps(exclude_resources=exclude_resources)

        return typing.cast(None, jsii.sinvoke(cls, "addAllAspects", [scope, props]))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-aspects-library-encryption-enforcement.EncryptionEnforcementAspectProps",
    jsii_struct_bases=[],
    name_mapping={"exclude_resources": "excludeResources"},
)
class EncryptionEnforcementAspectProps:
    def __init__(
        self,
        *,
        exclude_resources: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Common properties for all aspects in this module.

        :param exclude_resources: The resources to exclude from enforcement. Use a resource's ID to exclude a specific resource. Supports both CfnResource and L2 construct IDs. Default: []
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6af0f959c36276b797aa2a6693b922eb230029a894eabb5456a2cea0fbd4cda4)
            check_type(argname="argument exclude_resources", value=exclude_resources, expected_type=type_hints["exclude_resources"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exclude_resources is not None:
            self._values["exclude_resources"] = exclude_resources

    @builtins.property
    def exclude_resources(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The resources to exclude from enforcement.

        Use a resource's ID to exclude a specific resource.
        Supports both CfnResource and L2 construct IDs.

        :default: []
        '''
        result = self._values.get("exclude_resources")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EncryptionEnforcementAspectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class RDSEncryptionEnforcementAspect(
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-encryption-enforcement.RDSEncryptionEnforcementAspect",
):
    '''An aspect that enforces encryption on all RDS databases in the stack.

    Covers both single instances and clusters.
    '''

    def __init__(
        self,
        *,
        exclude_resources: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Constructs a new EncryptionEnforcementAspect.

        :param exclude_resources: The resources to exclude from enforcement. Use a resource's ID to exclude a specific resource. Supports both CfnResource and L2 construct IDs. Default: []
        '''
        props = EncryptionEnforcementAspectProps(exclude_resources=exclude_resources)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''Visits each construct in the stack and enforces encryption on RDS databases.

        :param node: - The construct to visit.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__313266e8b2fb20f372397e14e8ec129a2699ca40a50a7dd870a5c77a36026251)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))

    @builtins.property
    @jsii.member(jsii_name="excludeResources")
    def exclude_resources(self) -> typing.List[builtins.str]:
        '''The resources to exclude from enforcement.

        Use a resource's ID to exclude a specific resource.
        Supports both CfnResource and L2 construct IDs.

        :default: []
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludeResources"))


__all__ = [
    "EFSEncryptionEnforcementAspect",
    "EncryptionEnforcement",
    "EncryptionEnforcementAspectProps",
    "RDSEncryptionEnforcementAspect",
]

publication.publish()

def _typecheckingstub__19aeef40ce4bb911317e08c2b766f5ea7c1eb1f3729da90daa941c240c56c058(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e738479d84cc73bc794d6554ccf1576444abd88b913e87f265638a2f4155b4d6(
    scope: _constructs_77d1e7e8.IConstruct,
    *,
    exclude_resources: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6af0f959c36276b797aa2a6693b922eb230029a894eabb5456a2cea0fbd4cda4(
    *,
    exclude_resources: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__313266e8b2fb20f372397e14e8ec129a2699ca40a50a7dd870a5c77a36026251(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass
