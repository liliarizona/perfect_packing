#!/usr/bin/env python
import pepack

import sys
import os
import pprint
import pickle

def main():
	
	cLoc=os.getcwd()
	net_name='arpanet';
	
	#pepack.serializeAdjMat(cLoc + '/labNetworksAdjs/' + 'adjmat' + net_name + ".txt");
	#sys.exit(0);
	
	one_pack=pepack.getDic(cLoc + '/labNetworksPacks/' + net_name +'.perfect-packing');
	link_labels=pepack.getDic(cLoc + '/labNetworksAdjs/' + 'adjmat' + net_name + 'LinkLabel.txt');
	adj_mat=pepack.getDic(cLoc + '/labNetworksAdjs/' + 'adjmat' + net_name + 'Dic.txt');	
	
	num_nodes=len(one_pack);
	num_links=len(link_labels);
	
	source=2;
	dest=20;
	dfs_info=pepack.getDic(cLoc + '/labNetworksAdjs/' + 'adjmat' + net_name + "Des="+str(dest)+"DFS.txt");
	
	
	node_connectivity={};
	for node in range(1,num_nodes+1):
		temp=0;
		for x in range(1,len(one_pack[dest])+1):
			if node in one_pack[dest][x]:
				temp=temp+1;
		node_connectivity[node]=temp;
	
	failures={1:{3:5},2:{4:9}};
	routing_tables={};
	routing_tables=pepack.creatRoutingTable(source,dest,dfs_info['pre'],one_pack[dest]);
	#pprint.pprint(routing_tables);
	
	arc_info=pepack.creatArcPaires(one_pack[dest],link_labels);
	arc_index=arc_info['arc_index'];
	arc_pairs=arc_info['arc_pairs'];
	arc_recorder=arc_info['arc_recorder'];
	routed_info={};
	routed_info=pepack.routeOnePacket(source,dest,failures,arc_index,arc_recorder,arc_pairs,one_pack[dest],dfs_info['pre'],node_connectivity,routing_tables);
	
	path_length=len(routed_info);
	pstr=str(routed_info[1]);
	for one_entry in range(2,path_length+1):
		pstr=pstr+" --> "+str(routed_info[one_entry]);
	if routed_info[path_length]==dest:
		pstr=pstr+"\t"+"delivered";
	else:
		pstr=pstr+'\t'+"dropped";
	print pstr;
	#pprint.pprint(routed_info);
	#pprint.pprint(dfs_info['dist']);
	
if __name__ == '__main__':
    main()
