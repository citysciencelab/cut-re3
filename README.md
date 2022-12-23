# CUT RE3
The repository for the Masterportal addons and the OGC API Processes Backend that are developed for the third real world experiment in the CUT project.
In the future, this will also be the place where the participatory model will be hosted.

## Test Model Server
This flask server hosts a test agent-based model written in mesa that can be accessed via an API. 

### Model specifications
The model is a simple agent-based model that simulates bikes cycling in between various Stadtrad stations in Hamburg. Agents are generated based on the population of the various districts in Hamburg. 

The following are the parameters that influence the inner workings of the model. They can be passed on to the API (both via HTTP/POST and WebSockets) as a JSON object:
```
{
    "number_steps": 50,
    "number_iterations": 1,
    "agents_per_10000_inhabitants": 1
    
}
```
The parameters above are also the fallback standard parameters that will be chosen if they are not further specified. 


### Server API
There are two different ways to execute the model:
 
 1. **Via HTTP**. Retrieves either a GET Request (Standard parameters for the model run) or a POST request (Individual parameters can be passed on). The route to reach this is via `http://localhost:5001/http`
 1. **Via WebSockets**. In this way, http gateway timeouts are prevented and updates on the model run can be pushed from the server. The connection can be established with the route `ws://localhost:5001/socket`. In the file [websocket-test.html](test-model-server/websocket-test.html) the WebSocket connection can be tested in the browser. 



