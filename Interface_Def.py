import numpy as np
from scipy.spatial import distance_matrix

def interface_def(model_type, Interfaces, output_file, number_of_grains):

    element_def_path = f'{ output_file }/Elem_Def.dat'
    node_def_path = f'{ output_file }/Node_Def.dat'
    set_def_path = f'{ output_file }/Set_Def.dat'
    interfaceelem_path = f'{output_file}/Interface_Elem_Def.dat'

    output_node2_path = f'{ output_file }/Node_Sep_Def.dat'
    output_element2_path = f'{ output_file }/Elem_Sep_Def.dat'
    output_set2_path = f'{ output_file }/Set_Sep_Def.dat'

    def interfaceelement_voronoi_187(number_of_grains):
        def blank(val):
            leng = len(str(int(val)))
            space = 9 - leng
            for space in range(space):
                w2.write(" ")

        def assembling_Interface(x, y, elem_seq, temp):
            if np.array_equal(np.sort([int(x), int(y)]), np.array([0, 1])):
                temp = np.append(temp, elem_seq[4])
            if np.array_equal(np.sort([int(x), int(y)]), np.array([1, 2])):
                temp = np.append(temp, elem_seq[5])
            if np.array_equal(np.sort([int(x), int(y)]), np.array([0, 2])):
                temp = np.append(temp, elem_seq[6])
            if np.array_equal(np.sort([int(x), int(y)]), np.array([0, 3])):
                temp = np.append(temp, elem_seq[7])
            if np.array_equal(np.sort([int(x), int(y)]), np.array([1, 3])):
                temp = np.append(temp, elem_seq[8])
            if np.array_equal(np.sort([int(x), int(y)]), np.array([2, 3])):
                temp = np.append(temp, elem_seq[9])
            return temp

        temp5 = np.array([])
        temp6 = np.array([])
        temp7 = np.array([])

        for i in range(2, len(nepair), 3):  #

            nodes_in_elm1 = a3[int(nepair[i, 0]), :]
            nodes_in_elm2 = a3[int(nepair[i, 1]), :]

            node1_side1 = int(nepair[i - 2, 2])
            node2_side1 = int(nepair[i - 1, 2])
            node3_side1 = int(nepair[i, 2])

            node1_side2 = int(nepair[i - 2, 3])
            node2_side2 = int(nepair[i - 1, 3])
            node3_side2 = int(nepair[
                                  i, 3])  # node values nepair are taken from a3 itself and will be compared to a3 itself again, so factor of 3 should be considered

            for x in np.array([node1_side1, node2_side1, node3_side1]):
                temp5 = np.append(temp5.astype(int), np.where(nodes_in_elm1 == x))
            temp6 = np.append(temp6, [nodes_in_elm1[temp5]])
            temp6 = assembling_Interface(temp5[0], temp5[1], nodes_in_elm1, temp6)
            temp6 = assembling_Interface(temp5[1], temp5[2], nodes_in_elm1, temp6)
            temp6 = assembling_Interface(temp5[0], temp5[2], nodes_in_elm1, temp6)
            temp5 = np.array([])

            for x in np.array([node1_side2, node2_side2, node3_side2]):
                temp5 = np.append(temp5.astype(int), np.where(nodes_in_elm2 == x))
            temp7 = np.append(temp7, [nodes_in_elm2[temp5]])
            temp7 = assembling_Interface(temp5[0], temp5[1], nodes_in_elm2, temp7)
            temp7 = assembling_Interface(temp5[1], temp5[2], nodes_in_elm2, temp7)
            temp7 = assembling_Interface(temp5[0], temp5[2], nodes_in_elm2, temp7)
            temp5 = np.array([])

        temp6 = temp6.reshape(-1, 6)
        temp7 = temp7.reshape(-1, 6)
        attached = np.column_stack((temp6[:, 0:3], temp6[:, 2], temp7[:, 0:3], temp7[:, 2], temp6[:, 3:6], temp6[:, 5],
                                    temp7[:, 3:6], temp7[:, 5]))

        w2 = open(interfaceelem_path, 'w')
        new_elem_number = len(a3)
        index = len(no)
        # copy this section inside loop under new_elem_number+=1 to have one element under each element type
        index += 1
        number_of_grains += 1
        w2.write("ET," + str(number_of_grains) + ",INTER204\nMat," + str(number_of_grains) + "\nType," + str(number_of_grains) + "\n")
        w2.write("KEYO," + str(number_of_grains) + ",2,0\n")
        w2.write("Eblock,10,,,1\n")
        w2.write("(19i9)\n")
        # till here---------------
        for line in attached:
            new_elem_number += 1

            blank(new_elem_number)
            w2.write(str(int(new_elem_number)))

            for i in range(3):  # section type,real constant,material type
                blank(index)
                w2.write(str(int(number_of_grains)))

            blank(0)
            w2.write(str(int(0)))  # co-ordinate system

            for index_loop, value in enumerate(line):

                blank(value)
                w2.write(str(int(value)))
                if index_loop == 9:  # 10 nodes on a  line
                    w2.write("\n")
                    for i in range(5):
                        blank(0)
                        w2.write(str(0))

            w2.write("\n")
        w2.write("-1\n")
        w2.close()
        print("File 'Interface_Elem_Def.dat' has been saved")
    def import_elem_def_voronoi_187(x):
        a2 = np.array([])
        temp = np.zeros(10)
        n = 1
        noel = 0
        no = np.array([])
        for index, en in enumerate(x):
            if en.startswith("EN"):
                noel += 1
                en = en.split(",")
                temp[0] = int(en[2].strip(","))
                temp[1] = int(en[3].strip(","))
                temp[2] = int(en[4].strip(","))
                temp[3] = int(en[5].strip(","))
                temp[4] = int(en[6].strip(","))
                temp[5] = int(en[7].strip(","))
                temp[6] = int(en[8].strip(","))
                temp[7] = int(en[9].strip("\n"))
                continue

            elif en.startswith("EMORE"):
                en = en.split(",")
                temp[8] = int(en[1].strip(","))
                temp[9] = int(en[2].strip("\n"))

                a2 = np.append(a2, [temp[0:10]])

            elif en.startswith("Et"):
                no = np.append(no, noel)
        no = np.append(no, noel)
        a2 = a2.reshape(-1, 10)
        return a2, no
    def import_nodes(n):

        nonodes = 0
        nar = np.array([])
        for lines in n:
            nonodes += 1
            lines = lines.split(",")
            lines[1] = int(lines[1].strip(","))
            lines[2] = float(lines[2].strip(","))
            lines[3] = float(lines[3].strip(","))
            lines[4] = float(lines[4].strip("\n"))
            nar = np.append(nar, [lines[1], lines[2], lines[3], lines[4]])
            nar = nar.reshape(-1, 4)
        return nar, nonodes

    def neper_write_elements_187():
        def blank(val):
            leng = len(str(int(val)))
            space = 9 - leng
            for space in range(space):
                w2.write(" ")

        new_elem_number = 0
        index = 0
        w2 = open(output_element2_path, 'w')
        for line in a3:
            if new_elem_number == no[index]:
                index += 1
                if new_elem_number != 0:
                    w2.write(str(-1)+ "\n")
                w2.write("ET," + str(index) + ",SOLID187\nMat,1\nType," + str(index) + "\n")
                w2.write("eblock,19,solid,," + str(index) + "\n")
                w2.write("(19i9)\n")

            blank(1)  # material type
            w2.write(str(1))

            blank(index)  # element type
            w2.write(str(int(index)))

            for i in range(2):  # real constant,section type
                blank(index)
                w2.write(str(int(index)))

            for i in range(4):  # co-ordinate system,birth/death,solid model ref,element shape flag
                blank(0)
                w2.write(str(int(0)))

            blank(10)
            w2.write(str(int(10)))  # 10 number of nodes per elem
            blank(0)
            w2.write(str(int(0)))  # unused

            blank(new_elem_number + 1)
            w2.write(str(int(new_elem_number + 1)))

            for index_loop, value in enumerate(line):

                blank(value)
                w2.write(str(int(value)))
                if index_loop == 7:
                    w2.write("\n")
            new_elem_number += 1
            w2.write("\n")
        w2.write("-1\n")

        w2.close()
        print("File 'Elem_Sep_Def.dat' has been saved")

    def nepair_voronoi():
        contact3 = np.linspace(int(nodesarray[-1, 0]) - len(contact2) + 1, int(nodesarray[-1, 0]), num=len(contact2))
        # replacement nodes

        ellist1 = np.array([])
        ellist2 = np.array([])
        temp1 = np.array([])
        temp2 = np.array([])
        temp3 = np.array([])
        temp4 = np.array([])
        temp5 = np.array([])
        temp6 = np.array([])
        nepair = np.array([])
        for i in range(len(contact3)):
            temp1, temp2 = np.where(a3 == int(contact3[i]))
            for j in temp1:
                ellist1 = np.append(ellist1, [j, contact3[i]])
                temp3 = np.append(temp3, [nodesarr[int(a3[int(j)][0]) - 3], nodesarr[int(a3[int(j)][1]) - 3], \
                                          nodesarr[int(a3[int(j)][2]) - 3], nodesarr[int(a3[int(j)][3]) - 3]])
            ellist1 = ellist1.reshape(-1, 2)
            temp3 = temp3.reshape(-1, 4, 3)

            temp1, temp2 = np.where(a3 == int(contact2[i]))
            for l in temp1:
                ellist2 = np.append(ellist2, [l, contact2[i]])
                temp4 = np.append(temp4, [nodesarr[int(a3[int(l)][0]) - 3], nodesarr[int(a3[int(l)][1]) - 3], \
                                          nodesarr[int(a3[int(l)][2]) - 3], nodesarr[int(a3[int(l)][3]) - 3]])
            ellist2 = ellist2.reshape(-1, 2)
            temp4 = temp4.reshape(-1, 4, 3)

            # matching and checking
            for m in range(len(temp3)):
                for n in range(len(temp4)):
                    in_contact = distance_matrix(temp3[m], temp4[n])
                    temp5, temp6 = np.where(np.isclose(in_contact, np.zeros(4), atol=1e-4))
                    if len(temp5) == 3:
                        for o, p in zip(temp5, temp6):
                            nepair = np.append(nepair, [ellist1[int(m), 0], ellist2[int(n), 0],
                                                        a3[int(ellist1[int(m), 0]), int(o)],
                                                        a3[int(ellist2[int(n), 0]), int(p)]])

            temp3 = np.array([])
            temp4 = np.array([])
            ellist1 = np.array([])
            ellist2 = np.array([])

        nepair = nepair.reshape(-1, 4)
        nepair_temp = nepair[:, [2, 3]]
        nepair_temp = nepair_temp.reshape(-1, 6)
        nepair_temp = np.sort(nepair_temp)
        unique, index = np.unique(nepair_temp, axis=0, return_index=True)
        nepair = nepair.reshape(-1, 12)
        nepair = nepair[index]
        nepair = nepair.reshape(-1, 4)
        return nepair
    def blank(val):
        leng = len(str(int(val)))
        space = 10 - leng
        for space in range(space):
            w.write(" ")
    def sides():
        left = np.where(np.isclose(nodes[:, 0], np.amin(nodes[:, 0]), atol=1e-5))
        right = np.where(np.isclose(nodes[:, 0], dim_len, atol=1e-5))
        bottom = np.where(np.isclose(nodes[:, 1], np.amin(nodes[:, 1]), atol=1e-5))
        top = np.where(np.isclose(nodes[:, 1], dim_len, atol=1e-5))
        back = np.where(np.isclose(nodes[:, 2], np.amin(nodes[:, 2]), atol=1e-5))
        front = np.where(np.isclose(nodes[:, 2], dim_len, atol=1e-5))

        return np.asarray(left).T + 3, np.asarray(right).T + 3, np.asarray(bottom).T + 3, np.asarray(
            top).T + 3, np.asarray(back).T + 3, np.asarray(front).T + 3,
    def corner_nodes(nodes, dim_len, tol=1e-7):

        bottom_left_back = np.where((np.isclose(nodes[:, 0], np.amin(nodes[:, 0]), atol=tol)) & (
            np.isclose(nodes[:, 1], np.amin(nodes[:, 1]), atol=tol)) & (
                                        np.isclose(nodes[:, 2], np.amin(nodes[:, 2]), atol=tol)))
        top_left_back = np.where(
            (np.isclose(nodes[:, 0], np.amin(nodes[:, 0]), atol=tol)) & (np.isclose(nodes[:, 1], dim_len, atol=tol)) & (
                np.isclose(nodes[:, 2], np.amin(nodes[:, 2]), atol=tol)))
        bottom_right_back = np.where(
            (np.isclose(nodes[:, 0], dim_len, atol=tol)) & (np.isclose(nodes[:, 1], np.amin(nodes[:, 1]), atol=tol)) & (
                np.isclose(nodes[:, 2], np.amin(nodes[:, 2]), atol=tol)))
        top_right_back = np.where(
            (np.isclose(nodes[:, 0], dim_len, atol=tol)) & (np.isclose(nodes[:, 1], dim_len, atol=tol)) & (
                np.isclose(nodes[:, 2], np.amin(nodes[:, 2]), atol=tol)))
        bottom_left_front = np.where((np.isclose(nodes[:, 0], np.amin(nodes[:, 0]), atol=tol)) & (
            np.isclose(nodes[:, 1], np.amin(nodes[:, 1]), atol=tol)) & (np.isclose(nodes[:, 2], dim_len, atol=tol)))
        top_left_front = np.where(
            (np.isclose(nodes[:, 0], np.amin(nodes[:, 0]), atol=tol)) & (np.isclose(nodes[:, 1], dim_len, atol=tol)) & (
                np.isclose(nodes[:, 2], dim_len, atol=tol)))
        bottom_right_front = np.where(
            (np.isclose(nodes[:, 0], dim_len, atol=tol)) & (np.isclose(nodes[:, 1], np.amin(nodes[:, 1]), atol=tol)) & (
                np.isclose(nodes[:, 2], dim_len, atol=tol)))
        top_right_front = np.where(
            (np.isclose(nodes[:, 0], dim_len, atol=tol)) & (np.isclose(nodes[:, 1], dim_len, atol=tol)) & (
                np.isclose(nodes[:, 2], dim_len, atol=tol)))

        return np.array(bottom_left_back).T + 3, np.array(bottom_left_front).T + 3, np.array(
            bottom_right_back).T + 3, np.array(bottom_right_front).T + 3, np.array(top_left_back).T + 3, \
               np.array(top_left_front).T + 3, np.array(top_right_back).T + 3, np.array(top_right_front).T + 3

    if Interfaces == 'True':
        a2 = np.array([])
        x = open(element_def_path, 'r')

        no = np.array([])
        if model_type == 'Voronoi':
            a2, no = import_elem_def_voronoi_187(x)

        # finds the common nodes between grains and adds new nodes at the end of the
        # node defination with the same co-ordinates
        contact = []
        contact2 = np.array([])
        for s in range(len(no) - 2):
            grain1 = a2[int(no[s]):int(no[s + 1]), :]

            contact.append(np.intersect1d(np.unique(grain1.flatten()), a2[int(no[s + 1]):, :].flatten()))
            contact2 = np.append(contact2, np.intersect1d(grain1.flatten(), a2[int(no[s + 1]):, :].flatten()))
            # nodes those are being replaced
        contact2u = np.unique(contact2)

        n = open(node_def_path, "r")
        nodesarray, nonodes = import_nodes(n)

        nonodes2 = nonodes
        nodespair = []
        for nodes in contact2:
            nodestemp = nodesarray[int(nodes) - 3, :]
            nodesarray = np.vstack((nodesarray, np.array([int(nonodes + 3), nodestemp[1], nodestemp[2], nodestemp[3]],
                                                         ndmin=2).reshape(1, 4)))
            nodespair.append(str(nodes) + "," + str(nonodes + 3))
            nonodes += 1

        a3 = a2  # ---------------------important #a3=cp.copy(a2)
        ##################################################################
        # replaces the common nodes with the new nodes with same co-ordinates
        test = []
        for s in range(len(no) - 2):
            grain2 = a3[int(no[s]):int(no[s + 1]), :]
            for i in contact[s]:
                x1, y1 = np.where(grain2 == i)
                for s1, s2 in zip(x1, y1):
                    grain2[int(s1), int(s2)] = nonodes2 + 3
                nonodes2 += 1
            test.append(grain2)

        nd1 = open(output_node2_path, "w")
        for n in nodesarray:
            nd1.write("N,")
            nd1.write(str(int(n[0])) + "," + str(n[1]) + "," + str(n[2]) + "," + str(n[3]) + "\n")
        print("File 'Node_Sep_Def.dat' has been saved")
        nd1.close()

        if model_type == 'Voronoi':
            neper_write_elements_187()

        if Interfaces == 'True':
            n = open(output_node2_path, "r")
            nodesarr, lenarr = import_nodes(n)
            nodesarr = np.delete(nodesarr, 0, axis=1)
            n.close()

            # --------------------------trial part------------------------------

            if model_type == 'Voronoi':
                nepair = nepair_voronoi()
             # this can also be nepair_voronoi with Interfaceelement_voronoi_187
            # ------------------------------------trial end-----------------------

            if model_type == 'Voronoi':
                interfaceelement_voronoi_187(number_of_grains)
            del nepair

        ####################################################################
        # if the grains split, this introduces the iterface element in the Interfaces of split grains
        m = []
        check6 = 0
        check4 = 0

    if model_type == 'Voronoi':

        m = []
        check6 = 0
        check4 = 0

        if Interfaces == 'True':
            n = open(output_node2_path, "r")
            w = open(output_set2_path, "w")
        else:
            n = open(node_def_path, "r")
            w = open(set_def_path, "a")

        for node in n:
            node = node.split(",")
            m.append(node[1].strip(","))
            check4 = check4 + 1

        w.write("\nCMBLOCK, ALL_NODES ,NODE,    ")
        w.write(str(check4))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")
        written_nodes = set()
        for node in m:
            if node not in written_nodes:
                blank(node)
                w.write(node)
                check6 += 1
                if check6 == 8:
                    w.write("\n")
                    check6 = 0
                written_nodes.add(node)
        m.clear()
        del node

        # -----------------------------------------------
        # importing nodes
        if Interfaces == 'True':
            nodes_def = open(output_node2_path, 'r')
            elem_def = open(output_element2_path, 'r')
        else:
            nodes_def = open(node_def_path, 'r')
            elem_def = open(element_def_path, 'r')
            a2, no = import_elem_def_neper(elem_def)

        nodes, no_nodes = import_nodes(nodes_def)
        nodes = np.delete(nodes, 0, axis=1)
        dim_len = np.max(nodes)
        left, right, bottom, top, back, front = sides()
        bottom_left_back, bottom_left_front, bottom_right_back, bottom_right_front, top_left_back, top_left_front, top_right_back, top_right_front = corner_nodes(
            nodes, dim_len)
        # ---------------------------------------------
        index = 0
        new_elem_number = 0
        prev = 0
        check6 = 0

        for element in a2:
            if new_elem_number == no[index]:
                w.write("\nCMBLOCK,Grain_" + str(index + 1) + ",ELEM,   ")
                w.write(str(int(no[index + 1] - prev)))
                w.write("\n")
                w.write("(8i10)")
                w.write("\n")
                index += 1
                prev = no[index]
                check6 = 0

            blank(new_elem_number + 1)
            w.write(str(int(new_elem_number + 1)))
            check6 += 1

            if check6 == 8:
                w.write("\n")
                check6 = 0

            new_elem_number += 1

        celst = []

        check6 = 0
        w.write("\nCMBLOCK,BACK,NODE,   ")
        w.write(str(len(back)))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")

        for node in back:

            blank(node)
            w.write(str(int(node)))

            check6 = check6 + 1
            if check6 == 8:
                w.write("\n")
                check6 = 0

        check6 = 0
        w.write("\nCMBLOCK,FRONT,NODE,   ")
        w.write(str(len(front)))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")

        for node in front:

            blank(node)
            w.write(str(int(node)))

            check6 = check6 + 1
            if check6 == 8:
                w.write("\n")
                check6 = 0

        # -------------------------------------------------------------------------------

        check6 = 0
        w.write("\nCMBLOCK,BOTTOM,NODE,   ")
        w.write(str(len(bottom)))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")

        for node in bottom:

            blank(node)
            w.write(str(int(node)))

            check6 = check6 + 1
            if check6 == 8:
                w.write("\n")
                check6 = 0

        check6 = 0
        w.write("\nCMBLOCK,TOP,NODE,   ")
        w.write(str(len(top)))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")

        for node in top:

            blank(node)
            w.write(str(int(node)))

            check6 = check6 + 1
            if check6 == 8:
                w.write("\n")
                check6 = 0

        # ----------------------------------------------

        check6 = 0
        w.write("\nCMBLOCK,LEFT,NODE,   ")
        w.write(str(len(left)))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")

        for node in left:

            blank(node)
            w.write(str(int(node)))

            check6 = check6 + 1
            if check6 == 8:
                w.write("\n")
                check6 = 0

        check6 = 0
        w.write("\nCMBLOCK,RIGHT,NODE,   ")
        w.write(str(len(right)))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")

        for node in right:

            blank(node)
            w.write(str(int(node)))

            check6 = check6 + 1
            if check6 == 8:
                w.write("\n")
                check6 = 0
        check6 = 0
        w.write("\nCMBLOCK,Bottom_left_back,NODE,   ")
        w.write(str(len(bottom_left_back)))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")

        for node in bottom_left_back:

            blank(node)
            w.write(str(int(node)))

            check6 = check6 + 1
            if check6 == 8:
                w.write("\n")
                check6 = 0

        check6 = 0
        w.write("\nCMBLOCK,Bottom_left_front,NODE,   ")
        w.write(str(len(bottom_left_front)))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")

        for node in bottom_left_front:

            blank(node)
            w.write(str(int(node)))

            check6 = check6 + 1
            if check6 == 8:
                w.write("\n")
                check6 = 0

        check6 = 0
        w.write("\nCMBLOCK,Bottom_right_back,NODE,   ")
        w.write(str(len(bottom_right_back)))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")

        for node in bottom_right_back:

            blank(node)
            w.write(str(int(node)))

            check6 = check6 + 1
            if check6 == 8:
                w.write("\n")
                check6 = 0

        check6 = 0
        w.write("\nCMBLOCK,Bottom_right_front,NODE,   ")
        w.write(str(len(bottom_right_front)))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")

        for node in bottom_right_front:

            blank(node)
            w.write(str(int(node)))

            check6 = check6 + 1
            if check6 == 8:
                w.write("\n")
                check6 = 0

        check6 = 0
        w.write("\nCMBLOCK,Top_left_back,NODE,   ")
        w.write(str(len(top_left_back)))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")

        for node in top_left_back:

            blank(node)
            w.write(str(int(node)))

            check6 = check6 + 1
            if check6 == 8:
                w.write("\n")
                check6 = 0

        check6 = 0
        w.write("\nCMBLOCK,Top_left_front,NODE,   ")
        w.write(str(len(top_left_front)))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")

        for node in top_left_front:

            blank(node)
            w.write(str(int(node)))

            check6 = check6 + 1
            if check6 == 8:
                w.write("\n")
                check6 = 0

        check6 = 0
        w.write("\nCMBLOCK,Top_right_back,NODE,   ")
        w.write(str(len(top_right_back)))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")

        for node in top_right_back:

            blank(node)
            w.write(str(int(node)))

            check6 = check6 + 1
            if check6 == 8:
                w.write("\n")
                check6 = 0

        check6 = 0
        w.write("\nCMBLOCK,Top_right_front,NODE,   ")
        w.write(str(len(top_right_front)))
        w.write("\n")
        w.write("(8i10)")
        w.write("\n")

        for node in top_right_front:

            blank(node)
            w.write(str(int(node)))

            check6 = check6 + 1
            if check6 == 8:
                w.write("\n")
                check6 = 0

        # -------------------------------------------------------
        w.close()
        print("File 'Set_Sep_Def.dat' has been saved")

