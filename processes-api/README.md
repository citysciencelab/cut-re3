# Processes API for simulations

The /openapi endpoint describes this API and allows to call them interactively in the browser.
See https://dive.pygeoapi.io/standards/

If you want to retrieve the results, then you have to add the header
Accept: application/json

Example inputs for a job execution:

{
    "mode": "async",
    "inputs": {
        "simulation_name": "Blafoo Simsala Bim",
        "x": 2.6,
        "y": 8
    }
}
