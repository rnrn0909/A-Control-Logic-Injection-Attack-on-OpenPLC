# A-Control-Logic-Injection-Attack-on-OpenPLC
Good Night, and Good Luck: A Control Logic Injection Attack on OpenPLC

This will be published in March 2023. 

[[Demo Video]](https://youtu.be/rEBeV982gWQ)

[[Good Night, and Good Luck: A Control Logic Injection Attack on OpenPLC]](https://www.researchgate.net/publication/368958709_Good_Night_and_Good_Luck_A_Control_Logic_Injection_Attack_on_OpenPLC)
This tool is used to implement the attack presented in Good Night, and Good Luck: A Control Logic Injection Attack on OpenPLC. 


## Attacker Model
With help of MITRE ATT@CK

- T1555 Credentials from Password Stores
- T1040 Network Sniffing
- T1040 Unauthorized Password Reset
- T1110.002 Password Cracking
- T830 Man in the Middle (MitM)
- T0831 Manipulating the Control
- T8021 Modify Controller Tasking
- T0889 Modify Program
- T0842 Program Upload


## Usage
```
sudo python3 gngl.py -t {target IP address} -p {target port}
```

## Example Usage
```
sudo python3 gngl.py -t 127.0.0.1 -p 8080
```
