# -*- coding: utf-8 -*-
import block
import os
import operator
import hashlib
import time

KB = 1024
MB = KB * 1024
GB = MB * 1024
TB = GB * 1024



anchor_size = 48
d = 256
#q = 81919
#q = 56131
#q = 10331
#q = 1033
q = 811




# Rabin Hash를 이용해 값이 0 인 부분을 찾아 Anchor로 만든다.
# Rabin Hash는 anchor_size값을 길이로 한다.
# d는 ascii가 표현할 수 있는 범위 0~255를 포함 할 수 있는 256을 기본으로 한다.
# Rabin 해시 값은 큰 수가 나올 수 있기 때문에 q라는 큰 소수로 나누어 값을 줄인다.
# min_block_size를 이용하여 block의 최소 길이를 보장한다.
# max_block_size를 이용하여 block의 최대 길이를 제한하는데, 제한할 경우 뒤의 Anchor값들이 영향을 받으므로 고민(미구현)
# return : 앵커로 결정된 Table list
def Rabin_Karp_anchor(fullName, anchor_size, d, q, min_block_size):
    file_size = os.path.getsize(fullName)
    if file_size < anchor_size:
        return []

    file = open(fullName)
    text = file.read(anchor_size)
    file.close()


    n = file_size
    m = anchor_size
    h = pow(d,m-1)%q
    t = 0

    anchor_list = []
    for i in range(m): # preprocessing
        t = (d*t+ord(text[i]))%q

    s = 0
    last_anchor = -anchor_size

    s = s + anchor_size + min_block_size - 1
    while (s < n - m + 1):  # note the +1

        

        if t == 0 and last_anchor + anchor_size + min_block_size <= s: # check character by character
            compare_block = block.Compare_Block()

            compare_block.offset = [s, s + anchor_size]
            compare_block.sha_hash = SHA_hash(text)
            compare_block.type = "ANCHOR"

            anchor_list.append(compare_block)

            last_anchor = s

            # min_block_size 만큼 건너뛰어 보장

            s = s + anchor_size + min_block_size - 1
            if s + m > file_size:
                break


            t = 0

            file = open(fullName)
            file.seek(s)
            text = file.read(anchor_size)
            file.close()

            for i in range(m):  # preprocessing
                t = (d * t + ord(text[i])) % q

        if s < n-m:
            t = (t - h * ord(text[0])) % q  # remove letter s


            file = open(fullName)
            file.seek(s + m)
            text = text[1:] + file.read(1)

            file.close()

            t = (t * d + ord(text[-1])) % q  # add letter s+m
            t = (t + q) % q  # make sure that t >= 0

            s += 1

        else:
            break

    return anchor_list

# Rabin_Karp_Anchor함수를 통해 생성된 anchor_list를 인자로 사용하여, 해당 앵커를 기준으로 Block을 생성한다.
# Block은 하나의 덩어리로 Table을 구성하며, 이 때 rabin Hash, sha hash등의 값을 구하여 저장한다.
# return : Table로 구성된 Block과 Anchor list
def Rabin_Karp_split(fullName, anchor_size, d, q, anchor_list):
    block_anchor_list = []
    file_size = os.path.getsize(fullName)

    for i in range(len(anchor_list)):

        if i == 0:
            min_index = 0
            max_index = anchor_list[i].offset[0]

        else:
            min_index = anchor_list[i - 1].offset[1]
            max_index = anchor_list[i].offset[0]


        f = open(fullName)
        f.seek(min_index)
        text = f.read(max_index - min_index)
        f.close()

        compare_block = block.Compare_Block()
        compare_block.offset = [min_index, max_index]
        compare_block.sha_hash = SHA_hash(text)
        compare_block.type = "BLOCK"

        block_anchor_list.append(compare_block)

        block_anchor_list.append(anchor_list[i])

    # 마지막 블록 처리
    compare_block = block.Compare_Block()
    compare_block.type = "BLOCK"


    if len(anchor_list) >= 1:
        f = open(fullName)
        f.seek(max_index + anchor_size)
        text = f.read(file_size - (max_index + anchor_size))
        f.close()

        compare_block.offset = [max_index + anchor_size, file_size]
        compare_block.sha_hash = SHA_hash(text)

    else:
        f = open(fullName)
        text = f.read()
        f.close()

        compare_block.offset = [0, file_size]
        compare_block.sha_hash = SHA_hash(text)

    block_anchor_list.append(compare_block)

    return block_anchor_list



# text를 SHA hash 값으로 변환하는 함수
def SHA_hash(text):
    n = len(text)
    r = hashlib.sha256()
    #r.update(str(text).encode('utf-8'))
    r.update(str(text))
    sha_hash = r.hexdigest()

    return sha_hash



def BlockListCompare(FileFullName, new_compare_block_list, org_compare_block_list):

    org_last_find_pos = -1

    transfer_insert_list = []
    transfer_update_list = []

    for i in range(0, len(new_compare_block_list)):

        find = False

        for j in range(org_last_find_pos + 1, len(org_compare_block_list)):
            if new_compare_block_list[i].sha_hash == org_compare_block_list[j].sha_hash:

                start_offset = new_compare_block_list[i].offset[0]
                end_offset = new_compare_block_list[i].offset[1]

         
                transfer_update_block = block.Transfer_Block()
                transfer_update_block.type = "update"
                transfer_update_block.str = ""
                transfer_update_block.src_offset = org_compare_block_list[j].offset
                transfer_update_block.dst_offset = [start_offset, end_offset]

                #transfer_update_block.sha_hash = new_compare_block_list[j].sha_hash

                transfer_update_list.append(transfer_update_block)
            
                find = True

                org_last_find_pos = j

                break

        # 같은 블락 또는 앵커가 있음
        if find:
            pass

        # 같은 블락 또는 앵커가 없음
        else:
            start_offset = new_compare_block_list[i].offset[0]
            end_offset = new_compare_block_list[i].offset[1]

            f = open(FileFullName)
            f.seek(start_offset)
            block_str = f.read(end_offset - start_offset)
            f.close()

            transfer_insert_block = block.Transfer_Block()
            transfer_insert_block.type = "insert"
            transfer_insert_block.str = block_str
            transfer_insert_block.src_offset = []
            transfer_insert_block.dst_offset = [start_offset, end_offset]
           # transfer_insert_block.sha_hash = new_compare_block_list[i].sha_hash

            transfer_insert_list.append(transfer_insert_block)



    return transfer_insert_list, transfer_update_list


def reMakeBlock(transfer_insert_list, transfer_update_list):
    sorted_list = transfer_insert_list + transfer_update_list
    #sorted_list = sorted(sorted_list, key=operator.attrgetter('dst_offset'))


    return sorted_list


def CalcSimilarity(new_compare_block_list, org_compare_block_list):
    total_size = max(new_compare_block_list[-1].offset[1], org_compare_block_list[-1].offset[1])
    sum_of_same_block_size = 0

    org_last_find_pos = -1

    for i in range(0, len(new_compare_block_list)):
        for j in range(org_last_find_pos + 1, len(org_compare_block_list)):
            if new_compare_block_list[i].sha_hash == org_compare_block_list[j].sha_hash:
                sum_of_same_block_size += (new_compare_block_list[i].offset[1] - new_compare_block_list[i].offset[0])
                org_last_find_pos = j
                break


    similarity = round((sum_of_same_block_size / float(total_size)), 2)

    return similarity

