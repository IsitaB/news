# news
Mongodb sharded replicaset 

Start all instances
SSH into them

On the config servers, run `sudo mongod --config /etc/mongod.conf --fork`
On the shard servers, run `./startmongod.sh`
On the mongos server run `sudo mongos --config /etc/mongod.conf --fork`

Create a `.env` file with the MONGO_URI

In your terminal, run `source myvenv/bin/activate`

Run `python main.py` to run the script
