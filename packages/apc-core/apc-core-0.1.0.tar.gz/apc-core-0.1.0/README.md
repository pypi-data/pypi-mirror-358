# APC Core Library (Python)

This package implements the core state machines and message handling for the Agent Protocol Conductor (APC).

## Modules
- state_machine.py: Conductor & Worker state machines
- messages.py: Message classes (auto-generated from Protobuf)
- checkpoint.py: Checkpoint manager interface
- security.py: Security (mTLS/JWT) stubs
- __init__.py: Package init

## Usage
This library is intended to be used by transport adapters and agent SDKs.
