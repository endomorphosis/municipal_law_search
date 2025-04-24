# TODO for American Law Search


### Technical Todo

- [ ] Get sampling of citations.
    - [ ] 30 Bluebook citations minimum.
    - [ ] 385 Bluebook citations maximum.
- [ ] Add requested features
    - [ ] Implement Search History function
    - [ ] Create Filtering system  
    - [ ] Setup security measures
    - [ ] Increase specificity of searches (e.g. return 9.5% when asked about what the local sales tax is in Cheyenne, WY.)

- [ ] Search Result Return Optimization: Results Return < 100 milliseconds on average (parity with Google-search)
    - *Results Return*: The period of wall time it takes between when a non-blank search query is submitted and when a response is returned to the user.
    - [ ] Identify search speed bottlenecks.
        - *Bottleneck*: An operation that comprises 
        - [ ] Confirm or deny disk read from database as a bottleneck
        - [ ] Confirm or deny LLM SQL query creation time as a bottleneck
        - [ ] Confirm or deny creation of vector embedding for search query
        - [ ] Confirm or deny vector embedding search as a bottleneck
        - [ ] Confirm or deny unoptimized concurrency as a bottleneck
        - [ ] Research other potential bottlenecks
    - [ ] When identified, identify the following for each
        - [ ] 

- [ ] Concurrency Optimization: Number of Total Visitors Actively Using Site Functionality
    - Guard Metric: Search Results Return
    - Total monthly visitors for companies with less than 10 people gets 1,000 to 15,000 users a month

- [ ] Advanced Features: Make the program as similar to Google as possible.
    - [ ] Search via voice option
    - [ ] Search via image option
    - [ ] Advanced search options
        - [ ] Find pages with...
            - [ ] Partial string match (e.g. any of these words, all these words, type the important words)
            - [ ] Exact string match (e.g. this exact word or phrase, put exact words in quotes)
            - [ ] Partial string exclusion (e.g. none of these words)
        - [ ] Then narrow your results by...
             - [ ] Language
             - [ ] Region
             - [ ] Last Update
             - [ ] Site or domain (e.g. Building Codes, Appendices, current city's website, etc.)
             - [ ] Terms appearing
                - [ ] Anywhere in the results
                - [ ] Title
                - [ ] Text/HTML
                - [ ] Page URL
                - [ ] Links to the page
            - [ ] File-Type
        - [ ] Syntax for search must be identical to Google search's
        - [ ] Shortcuts

- [ ]

### Non-Technical TODO
- [ ] Get a .com domain for the website
- [ ] 

### In Progress

- [ ] N/A  

### Done ✓

- [x] N/A