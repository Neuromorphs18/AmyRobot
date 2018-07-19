# Amy G. Dala: Functional Amygdala Modeling Distributed Across Multiple Neuromorphics Hardwares

---

## Instructions for Running Amy
0.	Start Redis Server with correct configuration:
	'''
	$ redis-server /redis-stable/redis.conf
	'''
1.	SSH into Lego Mindstorm to activate ev3_link **(Terminal 1: frontend)**
	'''
	$ ssh robot@10.0.0.9
	$ ./ev3_link
	$ exit
	'''
2.	SSH into AIY raspberry pi and start the frontend **(Terminal 1: frontend)**
	'''
	$ ssh pi@10.0.0.8
	$ python ~/AmyRobot/frontend_aiy.py
	'''
3. 	SSH into an appropriate Loihi account (e.g. Terry's) with localhost forwarding **(Terminal 2: lateral)**
	'''
	$ ssh -L 8899:localhost:8899 terry@10.0.0.13
	'''
4.	SSH into the same account in a new terminal, then SSH into abr-user and run the driver service (kill run with 'ctrl-\') **(Terminal 3: Loihi monitor)**
	'''
	$ ssh terry@10.0.0.13
	$ ssh abr-user@loihimh
	$ cd boot_shim
	$ sudo ./run_n2driverservice_indef.sh
	'''
5. 	Open host on CPU **(Terminal 4: host)**
	'''
	$ source activate ev3
	$ nengo --port 8080 host_cpu.py
	'''
6.	Open lateral nucleus on Loihi (click link to open GUI) **(Terminal 2: lateral)**
	'''
	$ source activate loihi
	$ nengo --no-browser --backend nengo_loihi --port 8899 loihi_lateral.py
	'''
7.	Open basal nucleus on Spinnaker **(Terminal 5: basal)**
	'''
	$ source activate spinnaker
	$ nengo --backend nengo_spinnaker --port 8081
	'''
8.	Open central nucleus on Braindrop **(Terminal 6: central)**
	'''
	$ nengo --backend nengo_brainstorm --port 8082 central_brd.py
	'''
9.	Start various nengo GUIs!

To record data while running, make sure that there are no data files in the directory and simply replace ".py" with "_record.py" for each module.
