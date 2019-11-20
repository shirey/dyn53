##Dyn53 Dynamic DNS client for Route53

A dynamic DNS client to update an AWS Route53 based on the external IP address of the host where the client is running.

To use copy the dyn53.props.example file to dyn53.props and edit to provide the required properties.

Run with Python 3.x by installing the requirements in requirements.txt with `pip install -r requirements.txt` then run daily via cron or other execution scheduler with `python dyn53.py`.

