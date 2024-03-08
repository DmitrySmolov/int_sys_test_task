#!/bin/bash
start bash -c "python -m server.server"
sleep 1
start bash -c "python -m clients.client 1"
start bash -c "python -m clients.client 2"
