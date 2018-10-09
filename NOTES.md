#Reporter

Reporter, from report pipeline, is another iteration of the plutarch reporting
project. It aims to aleviate some of the difficulties faced during new report
production. Finally, the design has been made to work well with systems such as
Jenkins and work without connectivity.

##Report

- YAML configuraiton file
- Queries to be used
	- A list of queries from a specialized QUERY class
- Transformations
	- Query and report specific data transformations required to be handled by
      the output
- Artifact Production
	- A list of canned functions and report specific functions to produce data
- Output
	- Output functions
- Pipeline support
	- A report can define steps that are any one of the above steps
	- The report can run any one of the steps as a separate process 
	- Output of previous steps consumed by future steps if available, 
      debug data produced otherwise
	
	
##Query

- YAML configuration file
- Query with templated parameters
- Ability to tag a column for canned functions
- Target pretty output column names
- Data types for serialization, and debug data production
