import azure.functions as func
import azure.durable_functions as df
import logging

app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Orchestrator function
@app.orchestration_trigger(context_name="context")
def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info("Orchestrator started.")
    
    tasks = [
        context.call_activity("say_hello", "Tokyo"),
        context.call_activity("say_hello", "Seattle"),
        context.call_activity("say_hello", "London")
    ]

    results = yield context.task_all(tasks)
    logging.info(f"Orchestrator completed with results: {results}")
    
    return results

# Activity function
@app.activity_trigger(input_name="name")
def say_hello(name: str) -> str:
    logging.info(f"Activity function received name: {name}")
    return f"Hello {name}!"

# HTTP Starter Function
@app.route(route="orchestrators/start", methods=["GET", "POST"])
@app.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client: df.DurableOrchestrationClient) -> func.HttpResponse:
    instance_id = await client.start_new("orchestrator_function")
    
    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    
    return client.create_check_status_response(req, instance_id)
