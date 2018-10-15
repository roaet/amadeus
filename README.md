# AMADEUS

Beautiful, approachable, and scalable multi-part widget orchestra. Amadeus is a
metaphor-heavy cloud work-doer. Original intent is to speed up reporting on
large, disconnected data-sets by promoting guided, asynchronous processing with
an unmanaged collection of worker nodes. Thoughts on what can be done to expand
on the original intent has manifested, as per norm, to muddle the mixture.

Despite possible deviations the current MVP of Amadeus only knows about data
and the processes that can be run on it -- quickly.

> Gotta go fast

## Development Status

Compositions:
- (noun) Composition
    - Core Developing
    - EYAML Lexer in Progress
- (noun) Data Source
    - Core Developed
    - Needs Auth
- (verb) Action 
    - Core Developed
    - Needs Auth
- (verb-ish?) Basic Statement
    - Core Developed
    - Loops and Branching in design

Members:
- (member) Conductor
    - Core Developing
    - 'Teach' in Design
- (member) Player
    - Core Developing
    - 'Learn' in Design

Architecture:
- (arch) BUS(RabbitMQ)
    - Implemented, Needs Hardening
- (arch) Data Storage
    - In Design

##Composition

A composition is an EYAML (extended-YAML) format that is read by conductors to
control the work done by the players.
