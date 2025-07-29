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
