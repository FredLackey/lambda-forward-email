# lambda-forward-email
Forwards incoming messages to an external destination.  Original message is attached.  An optional prefix is added to the subject line (ie `FW:`, etc.);

## Environment Variables:

|  Name  |  Description  |
|--------|---------------|
|  `IncomingBucketName`  |  Name of bucket to retrieve saved message from.  |
|  `IncomingBucketPrefix`  |  Optional prefix of items stored in the incoming bucket.  |
|  `ForwardingEmail`  |  Fowarded messages are from this email address.  |
|  `RecipentEmail`  |  Target email address for forwarded messages.  |
|  `SubjectPrefix`  |  Optional prefix of subject of forwaded message (ie `FW:`, etc.).  |
|  `Region`  |  AWS Region name where all functionality resides (S3, Lamda, etc.).  |
