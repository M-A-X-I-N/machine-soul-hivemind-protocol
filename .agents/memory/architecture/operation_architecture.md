# Library-first operation architecture

V2-52 fixed the dependency/extension policy before Python operation implementation.

Canonical human-facing detail: [`../../../autonomic_affairs/docs/OPERATION_ARCHITECTURE.md`](../../../autonomic_affairs/docs/OPERATION_ARCHITECTURE.md).

Agent-critical rules:

- declarations describe; they never perform work;
- wrappers expose one application + one operation and delegate;
- the orchestrator calls atomic wrapper interfaces rather than bypassing them;
- generic engines may dispatch on generic `Operation` and declared strategy **type**, never on `application.id` for hidden bespoke behavior;
- strategy descriptors are data; shared handlers provide behavior;
- application-specific custom Python is an explicit final escape hatch and still reuses shared state/account/result/primitives;
- a second similar custom hook is evidence for a missing reusable strategy;
- operation context owns shared resolved runtime inputs; app code does not invent parallel host/account discovery;
- engines return semantic results; presentation occurs above them;
- native scripts own narrow native actions only.
