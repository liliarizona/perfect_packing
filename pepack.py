#!/usr/bin/env python
import extract
import os
import pprint
import pickle

def getOnePack(file_dir):
	perfect_packings = pickle.load(open(file_dir,'rb'))	
	#pprint.pprint(perfect_packings)
	return perfect_packings

def getDic(file_dir):
	return pickle.load(open(file_dir,'rb'))

def dfs(root, adj_mat):
	num_nodes=len(adj_mat);
	visited_node={};
	distance={};
	pre_node={};
	to_be_visited_node={root};
	
	my_inf=0;
	for x in range(1,num_nodes+1):
		for node in adj_mat[x]:
			my_inf=my_inf+adj_mat[x][node];
			#print str(x)+":"+str(node);
	my_inf=my_inf+1;
	
	for node in range(1,num_nodes+1):
		distance[node]=my_inf;
	distance[root]=0;
	to_be_visited_node_buff={};
	
	while len(visited_node)!=num_nodes:
		pStr=str(len(visited_node))+":";
		print pStr;
		for node in to_be_visited_node:
			for cand_node in adj_mat[node]:
				if cand_node not in visited_node:
					if distance[node]+adj_mat[node][cand_node] < distance[cand_node]:
						to_be_visited_node_buff[cand_node]=1;
						pre_node[cand_node]=node;
						distance[cand_node]=distance[node]+adj_mat[node][cand_node];
			visited_node[node]=1;
			print "\t"+str(node);
		to_be_visited_node=to_be_visited_node_buff;
		to_be_visited_node_buff={};
	
	pprint.pprint(distance);
	return {"pre":pre_node,"dist":distance};

def checkLinkStatus(input,output,failures):
	#return 1 if input->output has failed, otherwise return 0
	num_failures=len(failures);
	for x in range(1,num_failures+1):
		if (input==x and output==failures[x]) or (output==x and input==failures[x]):
			return 1;
	return 0;

def nextAvailableTree(input,failure_vector,trees):
	num_trees=len(trees);
	for x in range(0,num_trees):
		if (input in trees[x]) and (failure_vector[x]==0):
			return x;
	return 0;

def creatRoutingTable(source,dest,shortest_path_tree,pack):
	forwarding_table={};
	reverse_table={};
	reverse_recorder={};
	num_backup_trees=len(pack);
	num_nodes=len(shortest_path_tree)+1;
	
	for node in range(1,num_nodes+1):
		forwarding_table[node]={};
		reverse_table[node]={};
		reverse_recorder[node]={};
	
	for node in shortest_path_tree:
		forwarding_table[node][num_backup_trees+1]=shortest_path_tree[node];
		if num_backup_trees+1 not in reverse_table[shortest_path_tree[node]]:
			reverse_table[shortest_path_tree[node]][num_backup_trees+1]={};
			reverse_recorder[shortest_path_tree[node]][num_backup_trees+1]={};
		reverse_table[shortest_path_tree[node]][num_backup_trees+1][len(reverse_table[shortest_path_tree[node]][num_backup_trees+1])+1]=node;
		reverse_recorder[shortest_path_tree[node]][num_backup_trees+1][len(reverse_recorder[shortest_path_tree[node]][num_backup_trees+1])+1]=0;
	
	for one_pack in pack:
		for node in pack[one_pack]:
			forwarding_table[node][one_pack]=pack[one_pack][node];
			if pack[one_pack][node] != dest:
				if one_pack not in reverse_table[pack[one_pack][node]]:
					reverse_table[pack[one_pack][node]][one_pack]={};
					reverse_recorder[pack[one_pack][node]][one_pack]={};
				reverse_table[pack[one_pack][node]][one_pack][len(reverse_table[pack[one_pack][node]][one_pack])+1]=node;
				reverse_recorder[pack[one_pack][node]][one_pack][len(reverse_table[pack[one_pack][node]][one_pack])+1]=0;
	
	#pprint.pprint(pack[3]);
	#pprint.pprint(reverse_table);
	#pprint.pprint(reverse_recorder);
	out={};
	out['forwarding_table']=forwarding_table;
	out['reverse_table']=reverse_table;
	out['reverse_recorder']=reverse_recorder;
	return out;

def creatArcPaires(pack,link_labels):
	num_links=len(link_labels);
	num_arcs=2*num_links;
	arc_labels={};
	arc_labels_index={};
	for x in range(1,num_links+1):
		for input_node in link_labels[x]:
			arc_labels[x]={};
			arc_labels[num_links+x]={};
			arc_labels[x][input_node]=link_labels[x][input_node];
			arc_labels[num_links+x][link_labels[x][input_node]]=input_node;
			if input_node not in arc_labels_index:
				arc_labels_index[input_node]={};
			arc_labels_index[input_node][link_labels[x][input_node]]=x;
			if link_labels[x][input_node] not in arc_labels_index:
				arc_labels_index[link_labels[x][input_node]]={};
			arc_labels_index[link_labels[x][input_node]][input_node]=num_links+x;
	
	arc_recorder={};
	for a_pack in pack:
		for node_one in pack[a_pack]:
			node_two=pack[a_pack][node_one];
			if node_one not in arc_recorder:
				arc_recorder[node_one]={};
			arc_recorder[node_one][node_two]=a_pack;
	
	arc_pairs={};
	for x in range(1,num_arcs+1):
		arc_pairs[x]=0;
	for node_one in arc_recorder:
		for node_two in arc_recorder[node_one]:
			if node_two in arc_recorder:
				if node_one in arc_recorder[node_two]:
					arc_one=arc_labels_index[node_one][node_two];
					arc_two=arc_labels_index[node_two][node_one];
					arc_pairs[arc_one]=arc_two;
					arc_pairs[arc_two]=arc_one;
					pstr=str(arc_one)+"-"+str(arc_two);
					
	re={};
	re['arc_index']=arc_labels_index;
	re['arc_recorder']=arc_recorder;
	re['arc_pairs']=arc_pairs;
	return re;

def isFail(n1,n2,f):
	for x in f:
		for tn1 in f[x]:
			tn2=f[x][tn1];
			if (n1==tn1 and n2==tn2) or (n2==tn1 and n1==tn2):
				return 1;
	return 0;

def jumpToBackupTree(in_node,out_node_intheory,arc_index,arc_recorder,arc_pairs,forwarding_table):
	backup_tree=0;
	failed_arc_id=arc_index[in_node][out_node_intheory];
	failed_reverse_arc_id=arc_index[out_node_intheory][in_node];
	if arc_pairs[failed_arc_id]==failed_reverse_arc_id:
		backup_tree=arc_recorder[out_node_intheory][in_node];
	
	if backup_tree==0: # if there is no arc on the failed reverse arc, chose the first backup tree
		for tree in forwarding_table:
			backup_tree=tree;
			break;
	return backup_tree;

def findReverseArcTree(in_node,out_node,arc_pairs,arc_index,arc_recorder):
	tree=0;
	out_arc_id=arc_index[in_node][out_node];
	in_arc_id=arc_index[out_node][in_node];
	if arc_pairs[out_arc_id]==in_arc_id: #there is a tree on the reverse arc
		tree=arc_recorder[out_node][in_node];
	return tree;

def routeOnePacket(source,dest,failures,arc_index,arc_recorder,arc_pairs,pack,shortest_path_tree,node_connectivity,routing_tables):
	num_backup_trees=len(pack); #shortest_path_tree is the num_backup_trees+1 th tree.
	forwarding_table=routing_tables['forwarding_table'];
	reverse_table=routing_tables['reverse_table'];
	reverse_recorder=routing_tables['reverse_recorder'];
	failure_recorder_at_node=routing_tables['forwarding_table']; #this is going to be used to solve the issue in case 3. it marks if a node has seen a failure, so that low connected node knows when to switch reverse trees
	tree_failure_vector={}; #if backup tree 1 failed, tree_failure_vector[1]=1,otherwise 0;
	for x in range(1,num_backup_trees+2):
		tree_failure_vector[x]=0;
	
	expected_connectivity=node_connectivity[dest];
	path_length=0;
	path_status=0;
	path={};
	
	reverse=0;
	reverse_reverse=0;
	current_tree=num_backup_trees+1; #start from the shoretest path tree
	
	#pprint.pprint(routing_tables);
	
	in_node=source;
	path[len(path)+1]=in_node;
	count=0;
	while in_node != dest and count<10000:
		count=count+1;
		if current_tree==num_backup_trees+1: # on shortest path tree
			if reverse==0: #not in reverse process
				out_node_intheory=forwarding_table[in_node][current_tree];
				fail_label=isFail(in_node,out_node_intheory,failures);
				if fail_label: #out arc is failed
					tree_failure_vector[current_tree]=1;
					if node_connectivity[in_node] < expected_connectivity: #failure found in a low connected node, start reverse process
						reverse=1;
						for one_choice in reverse_table[in_node][current_tree]:
							out_node=reverse_table[in_node][current_tree][one_choice];
							temp_label=isFail(in_node,out_node,failures);
							if temp_label==0:
								reverse_recorder[in_node][current_tree][one_choice]=1;
								in_node=out_node;
								path[len(path)+1]=in_node;
								break;
						continue;
					else: #failure found in a high connected node, forward on a backup tree. make sure to forward on the backup tree if there is a backup tree using the reverse arc of the failed arc.
						#chosed_backup_tree=jumpToBackupTree(in_node,out_node_intheory,arc_index,arc_recorder,arc_pairs,forwarding_table[in_node]);
						for one_backup_tree in forwarding_table[in_node]:
							current_tree=one_backup_tree;
							break;
						continue;
				else:	#out arc is valid, forward on that arc
					in_node=out_node_intheory;
					path[len(path)+1]=in_node;
					continue;
			else: # in reverse process
				if reverse_reverse==0: #not in reverse_reverse process
					if node_connectivity[in_node] < expected_connectivity: # low connected node, keep doing reverse process
						if current_tree in reverse_table[in_node]:
							flag=0;
							for node_of_one_reverse_arc in reverse_table[in_node][current_tree]:
								temp_label=isFail(in_node,node_of_one_reverse_arc,failures);
								if temp_label==0:		
									reverse_recorder[in_node][current_tree][node_of_one_reverse_arc]=1;
									in_node=node_of_one_reverse_arc;
									path[len(path)+1]=in_node;
									flag=1;
									break;
							if flag==0: #none of reverse arc is valid, inital reverse_reverse process
								reverse_reverse=1;
								continue;
								
						else: #no subtree to reverse, initial reverse_reverse process
							reverse_reverse=1;
							continue;
					else: #reach a high connected node, end reverse process, go to a backup tree
						reverse=0;
						for one_backup_tree in forwarding_table[in_node]:
							current_tree=one_backup_tree;
							break;
						continue;
				else: #in reverse_reverse process
					#check if subtree has been exhausted reversed, if no, chonse another child to reverse, otherwise, reverse reverse to parent node.
					flag=0;
					for one_child in reverse_table[in_node][current_tree]:
						if reverse_recorder[in_node][current_tree][one_child]==0: # found a child to be in reverse process, reverse on that child
							temp_label=isFail(in_node,reverse_table[in_node][current_tree][one_child],failures);
							if temp_label==0: # the arc is valid
								reverse_reverse=0;
								reverse_recorder[in_node][current_tree][one_child]=1;
								in_node=reverse_table[in_node][current_tree][one_child];
								path[len(path)+1]=in_node;
								flag=1;
								break;
					if flag==0: # no child to further reverse, send package to parent node
						in_node=forwarding_table[in_node][current_tree];
						path[len(path)+1]=in_node;
					continue;
		else: # on a backup tree
			if reverse==0: #not in reverse process
				out_node_intheory=forwarding_table[in_node][current_tree];
				fail_label=isFail(in_node,out_node_intheory,failures);
				if fail_label==0: #forwarding arc is valid, forward on it
					in_node=out_node_intheory;
					path[len(path)+1]=in_node;
					continue;
				else: #forwarding arc has failed
					tree_failure_vector[current_tree]=1; #mark the failed tree
					if node_connectivity[in_node] < expected_connectivity: #failure found at a low connected node
						temp_tree=findReverseArcTree(in_node,out_node_intheory,arc_pairs,arc_index,arc_recorder);
						if temp_tree==0: #no backup tree using the failed incoming arc, initial reverse process
							for one_choice in reverse_table[in_node][current_tree]:
								one_child=reverse_table[in_node][current_tree][one_choice];
								temp_label=isFail(in_node,one_child,failures);
								if temp_label==0: #found a valid reverse arc, note that there is at least one valid reverse arc anyway
									reverse=1;
									reverse_recorder[in_node][current_tree][one_choice]=1;
									in_node=one_child;
									path[len(path)+1]=in_node;
									break;
							continue;
						else: #there is a backup tree using the incoming failed arc, switch to that backup tree
							failure_recorder_at_node[in_node][current_tree]=1;
							current_tree=temp_tree;
							continue;
					else: #failure found at a high connected node, switch backup tree, if no tree to switch, drop the packet
						flag=0;
						for one_tree in forwarding_table[in_node]:
							if tree_failure_vector[one_tree]==0:
								current_tree=one_tree;
								flag=1;
								break;
						if flag==0: #no tree to switch to, drop the packet
							path_status="dropped";
							return path;
						continue;
			else: # in reverse process
				if node_connectivity[in_node] < expected_connectivty: # still in at a low connected node
					if reverse_reverse==0: #not in reverse_reverse process
						flag=0;
						for one_choice in reverse_table[in_node][current_tree]:
							one_out_node=reverse_table[in_node][current_tree][one_choice];
							temp_label=isFail(in_node,one_out_node,failures);
							if temp_label==0: #a valid reverse arc has been found
								in_node=one_out_node;
								path[len(path)+1]=in_node;
								flag=1;
								break;
						if flag==0: # no valid reverse arc has been found, check if backup trees has been switched here before
							for one_choice in reverse_table[in_node][current_tree]:
								temp_out_node=reverse_table[in_node][current_tree][one_choice];
								tree_of_reverse_arc=findReverseArcTree(in_node,temp_out_node,arc_pairs,arc_index,arc_recorder);
								if tree_of_reverse_arc != 0: # there is a tree on the reverse arc
									if failure_recorder_at_node[in_node][tree_of_reverse_arc]==1: # the tree on the reverse arc was detected to be failed at this node
										current_tree=tree_of_reverse_arc;
										flag=1;
										break;
						if flag==0: # no where to reverse, initial reverse reverse process
							reverse_reverse=1;
							in_node=forwarding_table[in_node][current_tree];
							path[len(path)+1]=in_node;
							flag=1;
						continue;
					else: #in reverse_reverse process
						flag=0;
						for one_choice in reverse_table[in_node][current_tree]: # try to switch a child to reverse
							one_child=reverse_table[in_node][current_tree][one_choice];
							temp_label=isFail(in_node,one_child,failures);
							if temp_label==0 and reverse_recorder[in_node][current_tree][one_choice]==0: #found another child to reverse
								reverse_reverse=0;
								in_node=one_child;
								path[len(path)+1]=in_node;
								flag=1;
								break;
						if flag==0: #try to switch a backup tree if a failure has been detected here before
							for one_choice in reverse_table[in_node][current_tree]:
								one_child=reverse_table[in_node][current_tree][one_choice];
								temp_label=isFail(in_node,one_child,failures);
								tree_of_reverse_arc=findReverseArcTree(in_node,one_child,arc_pairs,arc_index,arc_recorder);
								if temp_label==0 and failure_recorder_at_node[in_node][tree_of_reverse_arc]==1:
									reverse_reverse=0;
									current_tree=tree_of_reverse_arc;
									flag=1;
									break;
						if flag==0: #no where to reverse, reverse reverse to parent
							in_node=forwarding_table[in_node][current_tree];
							path[len(path)+1]=in_node;
							flag=1;
						continue;
				else: #reach a high connected node, end reverse process, switch backup tree if there is any
					reverse=0;
					flag=0;
					for one_tree in forwarding_table[in_node]:
						if tree_failure_vector[one_tree]==0:
							current_tree=one_tree;
							flag=1;
							break;
					if flag==0: #no tree to switch to, drop the packet
						path_status="dropped";
						return path;
					continue;

	return path;
	
'''
def routeOnePackage(source,dest,failures,pack,link_labels,shortest_path_tree,node_connectivity):
	path_length=0;
	in_node=source;
	out_node=source;
	num_backup_trees=len(pack);
	#calculate expected connectivity
	expect_connectity=node_connectivity[source];

	re=0;
	
	failure_vector={};
	for x in range(1,num_backup_trees+1):
		failure_vector[x]=0; #failure[1]=0 means tree 1 hasn't failed yet, otherwise failure[1]=1
	failure_vector[num_backup_trees+1]=0; # the num_backup_trees+1 tree is the shortest path tree
	current_tree=num_backup_trees+1; # always start from the shortest path tree
	
	all_trees={};
	for x in range(1, num_backup_trees+1):
		all_trees[x]=pack[x];
	all_trees[num_backup_trees+1]=shortest_path_tree;
	
	r_label=0;
	rr_label=0;
	link_failure_label=0;
	#pprint.pprint(all_trees);
	
	while in_node!=dest:
		if current_tree==num_backup_trees+1: # on shortest path tree
			theory_out_node=all_trees[current_tree][in_node];
			link_failure_label=checkLinkStatus(in_node,theory_out_node,failures);
			if link_failure_label: # the out link on the shortest path tree has failed, one should jump to backup tree.
				failure_vector[num_backup_trees+1]=1; # mark the failure
				# find the backup tree to forward on
				backup_tree=nextAvailableTree(in_node,failure_vector,all_trees);
				if backup_tree !=0: # there is a backup tree to jump to
					current_tree=backup_tree;
				else: # no backup tree to jump to, drop the package
					return 0;
			else: # out link on the shortest path tree is valid, forward on it
				path_length=path_length+1; #path length++
				in_node=theory_out_node; #update in_node
		else: #on backup tree
			if node_connectivity[in_node] >= expected_connectivity:
				#case 1
				return 1;
			else:
				if r==0:
					#case 2
					return 2;
				else:
					if rr==0:
						#case 3
						return 3;
					else:
						#case 4
						return 4;
	
	re=path_length;
	return re;
'''
	
	
def serializeAdjMat(file_dir):
	outDic={};
	linkArr={};
	node=0;
	file = open(file_dir,'rb')
	while 1:
		#if node==1:
		#	break
		line = file.readline()
		if not line:
			break
		else:
			node=node+1;
			outDic[node]={};
			oneAdj=line.split();
			count=0;
			for temp in oneAdj:
				count=count+1;
				if temp == '1':
					#print (node,count);
					outDic[node][count]=1;
	pprint.pprint(outDic);
	label=1;
	for node1 in outDic:		
		for node2 in outDic[node1]:
			if node2>node1:
				linkArr[label]={};
				linkArr[label][node1]=node2;
				label=label+1;
	pprint.pprint(linkArr);
	
	out_dir=file_dir.replace('.txt', 'Dic.txt');
	f1 = open(out_dir,"wb")
	pickle.dump(outDic, f1)
	f1.close()
	out_dir=file_dir.replace('.txt', 'LinkLabel.txt');
	f1 = open(out_dir,"wb")
	pickle.dump(linkArr, f1)
	f1.close()
		
		
		