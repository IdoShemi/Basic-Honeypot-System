# Honeypot System

Developed by: Ido Shemi, Niv Aderet

This projects was created to answer the problem that traditional security defenses sometimes fail to detect cyberattacks, leaving systems vulnerable to attackers. The solution is to use networks of traps to lure attackers with decoy systems, enabling real-time threat analysis and improved defense strategies without endangering actual assets.


## How to run the project:
1. Clone the repository into your own computer. 
2. Add the configurations files and the keys files.
3. Run the following commands to build the docker images: 
```
docker build -f Dockerfile.website -t website:latest .
docker build -f Dockerfile.ssh -t ssh:latest .
docker build -f Dockerfile.reporting -t reporting:latest .
```
4. Use Run the following commands to run the images and make them into containers:
```
docker run -d -p 5000:5000 reporting:latest
docker run -d -p 2222:2222 ssh:latest
docker run -d -p 30760:30760 website:latest
```

5. Now you will be able to access the services using the following credentials: 
```
SSH: localhost, Walter: admin, pass: White!
FTP: localhost, user: Donald, pass: Duck20
Website: localhost, user: Niv pass: nivniv123
Reporting_website: localhost, user: Admin_Fusion pass: NivIdo123!
```

6. Run the ftp.py file from the services directory while making sure the Hoenypot directory is the workdir. 

**Note:** Assuming the attacker got an access to a pc in the organization and got the credentials for the ssh service, there we will begin the flow.


Plan for future: 
We encountered an issue with setting up a Docker container for FTP because the range of client ports was too extensive. Many of these ports were already in use, making it impractical to expose all necessary ports unless we used a machine with no other applications, like an AWS EC2 instance. After extensively reviewing the source code of pyftpdlib, specifically at: https://github.com/giampaolo/pyftpdlib/blob/master/pyftpdlib/handlers.py, we identified a potential lead in the line: self.remote_ip, self.remote_port = self.socket.getpeername()[:2]. This requires further investigation into both pyftpdlib and the socket library. Given the time constraints, we've decided to maintain the setup locally for the time being.