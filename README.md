# My Redis
This is a coding project to demonstrate fundamental understanding of software engineering, source control, and the submission/review process involved with working in a collaborative programming environment.
The goal of this project is to answer the following tech challenge prompt:


**Overview:**


In a language of your choice, using only its stdlib, create an in-memory key-value store that supports Redis wire protocol’s GET, DEL and SET. Both keys and values may be of any primitive type.

 

Success Metrics
While running your solution, the following commands respond as such:

$ start solution

$ redis-cli set x 1

OK

$ redis-cli get x

“1”

$ redis-cli del x

(integer) 1

$ redis-cli get x

(nil)

 

OS resources do not leak under sustained use (specifically memory and file descriptors)


Unsupported commands receive a response indicating they are not supported

Resources:
Redis Wire Protocol reference - https://redis.io/topics/protocol

This project was written in Python and runs locally in its current form. GET, DEL, and SET commands operate as intended with most options functional. Future additions will include time locking options included with SET commands.
