# APC Core Library (Python)

The `apc-core` package provides the foundational state machines, message handling, and checkpointing logic for the Agent Protocol Conductor (APC). It is the heart of the APC protocol, enabling robust, decentralized orchestration of distributed AI agents.

## Key Features
- **Conductor & Worker State Machines:** Drive agent workflows, task sequencing, and dynamic leadership handoff.
- **Protobuf Message Handling:** Typed, cross-language messages for reliable agent communication.
- **Checkpoint Manager:** Pluggable backends (in-memory, Redis, S3) for resilient state recovery and failover.
- **Security Stubs:** Ready for mTLS and JWT-based authentication and policy enforcement.
- **Extensible Design:** Easily integrate with custom transports, business logic, or LLMs.

## Modules
- `state_machine.py`: Conductor & Worker state machines
- `messages/`: Message classes (auto-generated from Protobuf)
- `checkpoint.py`: Checkpoint manager interface & implementations
- `security.py`: Security (mTLS/JWT) stubs
- `__init__.py`: Package init

## Minimal Example
```python
from apc_core.state_machine import Conductor, Worker
from apc_core.checkpoint import InMemoryCheckpointManager

# Initialize a checkpoint manager
checkpoint_mgr = InMemoryCheckpointManager()

# Create a Conductor agent
conductor = Conductor(checkpoint_manager=checkpoint_mgr)

# Create a Worker agent
worker = Worker()

# (See examples/ for full agent implementations and orchestration logic)
```

## Usage
This library is intended to be used by transport adapters and agent SDKs. For end-to-end examples and advanced usage, see the [main documentation](../docs/documentation.md) and the [examples/](../examples/) directory.

---

For protocol details, see [apc-proto/apc.proto](../apc-proto/apc.proto).
