#! /usr/bin/python3

import sys
import struct
import socket

MAX_ID_LENGTH = 12
TOKEN_SIZE = 64
SAS_SIZE = 80

ITRequest = 1
ITResponse = 2
ITValidation = 3
ITStatus = 4

GTRequest = 5
GTResponse = 6
GTValidation = 7
GTStatus = 8

ERROR = 256

INVALID_MESSAGE_CODE = 1
INCORRECT_MESSAGE_LENGTH = 2
INVALID_PARAMETER = 3
INVALID_SINGLE_TOKEN = 4
ASCII_DECODE_ERROR = 5

def handleError(response):
    error_type = struct.unpack(">H", response[2:4])[0]
    if error_type == INVALID_MESSAGE_CODE:
        raise RuntimeError("INVALID_MESSAGE_CODE")
    elif error_type == INCORRECT_MESSAGE_LENGTH:
        raise RuntimeError("INCORRECT_MESSAGE_LENGTH")
    elif error_type == INVALID_PARAMETER:
        raise RuntimeError("INVALID_PARAMETER")
    elif error_type == INVALID_SINGLE_TOKEN:
        raise RuntimeError("INVALID_SINGLE_TOKEN")
    elif error_type == ASCII_DECODE_ERROR:
        raise RuntimeError("ASCII_DECODE_ERROR")
    else:
        raise RuntimeError("Unknown Error: Error code = {}".format(error_type))
    
    exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: {} <host> <port> <command>".format(sys.argv[0]))
        exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    command = sys.argv[3]

    is_ipv6 = False
    try:
        socket.inet_pton(socket.AF_INET6, host)
        is_ipv6 = True
    except:
        pass

    client_socket = socket.socket(socket.AF_INET6 if is_ipv6 else socket.AF_INET,
                                  socket.SOCK_DGRAM)
    
    if command == "itr":
        if len(sys.argv) != 6:
            print("Usage: {} <host> <port> <command>".format(sys.argv[0]))
            print("Command:")
            print("itr <id> <nonce>")
            exit(1);
        
        id = sys.argv[4]
        nonce = int(sys.argv[5])

        if len(id) > MAX_ID_LENGTH:
            raise RuntimeError("ID length too big")

        id = id.ljust(MAX_ID_LENGTH)

        request_type = struct.pack("H", socket.htons(ITRequest))
        request_id = id.ljust(MAX_ID_LENGTH).encode("ascii")
        request_nonce = struct.pack("I", socket.htonl(nonce))

        request = request_type + request_id + request_nonce

        client_socket.sendto(request, (host, port))

        response, _ = client_socket.recvfrom(82)
        response_type = struct.unpack("H", response[:2])[0]
        response_type = socket.ntohs(response_type)
        
        if response_type == ERROR:
            handleError(response)
        elif response_type != ITResponse:
            raise RuntimeError("Unexpected Error: Response = {}".format(response_type))
            exit(1)

        response_id, response_nonce, response_token = struct.unpack("{}sI{}s".format(MAX_ID_LENGTH, TOKEN_SIZE), response[2:])
        response_nonce = socket.ntohl(response_nonce)

        print("{}:{}:{}".format(response_id.decode("ascii").strip(), response_nonce, response_token.decode("ascii")))

    elif command == "itv":
        if len(sys.argv) != 5:
            print("Usage: {} <host> <port> <command>".format(sys.argv[0]))
            print("Command:")
            print("itv <SAS>")
            exit(1);
    
        sas = sys.argv[4]
        id, nonce, token = sas.split(":")
        nonce = int(nonce)

        request_type = struct.pack("H", socket.htons(ITValidation))
        request_id = id.ljust(MAX_ID_LENGTH).encode("ascii")
        request_nonce = struct.pack("I", socket.htonl(nonce))
        request_token = token.encode("ascii")

        request = request_type + request_id + request_nonce + request_token

        client_socket.sendto(request, (host, port))

        response, _ = client_socket.recvfrom(83)
        response_type = struct.unpack("H", response[:2])[0]
        response_type = socket.ntohs(response_type)
        
        if response_type == ERROR:
            handleError(response)
        elif response_type != ITStatus:
            raise RuntimeError("Unexpected Error: Response Code: {}".format(response_type))
            exit(1)

        response_status = struct.unpack("B".format(MAX_ID_LENGTH, TOKEN_SIZE), response[-1:])[0]

        print(response_status)

    elif command == "gtr":
        if len(sys.argv) < 5:
            print("Usage: {} <host> <port> <command>".format(sys.argv[0]))
            print("Command:")
            print("gtr <N> <SAS-1> <SAS-2> ... <SAS-N>")
            exit(1);
    
        n = int(sys.argv[4])
        members = sys.argv[5:]

        request = struct.pack("H", socket.htons(GTRequest))
        request += struct.pack("H", socket.htons(n))
        for sas in members:
            member_id, member_nonce, member_token = sas.split(":")
            request += member_id.ljust(MAX_ID_LENGTH).encode("ascii")
            request += struct.pack("I", socket.htonl(int(member_nonce)))
            request += member_token.encode("ascii")

        client_socket.sendto(request, (host, port))

        response, _ = client_socket.recvfrom(len(request) + TOKEN_SIZE)

        response_type = struct.unpack("H", response[:2])[0]
        response_type = socket.ntohs(response_type)
        
        if response_type == ERROR:
            handleError(response)
        elif response_type != GTResponse:
            raise RuntimeError("Unexpected Error: Response Code: {}".format(response_type))
            exit(1)

        response_n = struct.unpack("H", response[2:4])[0]
        response_n = socket.ntohs(response_n)
        
        gas = ""
        for i in range(response_n):
            sas = response[4 + i * SAS_SIZE: 4 + (i+1) * SAS_SIZE]
            sas_id, sas_nonce, sas_token = struct.unpack("{}sI{}s".format(MAX_ID_LENGTH, TOKEN_SIZE), sas)
            sas_nonce = socket.ntohl(sas_nonce)

            gas += "{}:{}:{}+".format(sas_id.decode("ascii").strip(), sas_nonce, sas_token.decode("ascii"))

        response_token = struct.unpack("{}s".format(TOKEN_SIZE), response[-TOKEN_SIZE:])[0].decode("ascii")
        gas += "{}".format(response_token)

        print(gas)

    elif command == "gtv":
        if len(sys.argv) != 5:
            print("Usage: {} <host> <port> <command>".format(sys.argv[0]))
            print("Command:")
            print("gtv <GAS>")
            exit(1);

        gas = sys.argv[4]
        gas = gas.split("+")
        members = gas[:-1]
        token = gas[-1]
        n = len(members)

        request = struct.pack("H", socket.htons(GTValidation))
        request += struct.pack("H", socket.htons(n))
        for sas in members:
            member_id, member_nonce, member_token = sas.split(":")
            request += member_id.ljust(MAX_ID_LENGTH).encode("ascii")
            request += struct.pack("I", socket.htonl(int(member_nonce)))
            request += member_token.encode("ascii")
        request += token.encode("ascii")

        client_socket.sendto(request, (host, port))

        response, _ = client_socket.recvfrom(len(request)+1)

        response_type = struct.unpack("H", response[:2])[0]
        response_type = socket.ntohs(response_type)
        
        if response_type == ERROR:
            handleError(response)
        elif response_type != GTStatus:
            raise RuntimeError("Unexpected Error: Response Code: {}".format(response_type))
            exit(1)

        response_status = struct.unpack("B".format(MAX_ID_LENGTH, TOKEN_SIZE), response[-1:])[0]

        print(response_status)

    else:
        print("Usage: {} <host> <port> <command>".format(sys.argv[0]))
        print("Commands:")
        print("itr <id> <nonce>")
        print("itv <SAS>")
        print("gtr <N> <SAS-1> <SAS-2> ... <SAS-N>")
        print("gtv <GAS>")
        exit(1)

    exit(0)