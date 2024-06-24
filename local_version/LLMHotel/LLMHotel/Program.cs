using LLama.Common;
using LLama;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.DependencyInjection;
using System.Collections.Generic;

var builder = WebApplication.CreateBuilder(args);

string modelPath = "C:\\Users\\kerem\\Desktop\\webApi\\LLAMA_Deneme\\Model\\llama-2-7b-guanaco-qlora.Q4_K_M.gguf";

var parameters = new ModelParams(modelPath)
{
    ContextSize = 1024
};
using var model = LLamaWeights.LoadFromFile(parameters);

using var context = model.CreateContext(parameters);
var ex = new InteractiveExecutor(context);
ChatSession session = new ChatSession(ex);
string txt = "";
var prompt = @"
Prompt Hidden
";



foreach(var text in session.Chat(prompt, new InferenceParams { Temperature = 0.6f, AntiPrompts = new List<string> { "User:" } }))
{
    txt = text;
}



var app = builder.Build();


app.MapPost("/chat", async (HttpContext httpContext) =>
{
    // Read the request body
    string requestText = await new StreamReader(httpContext.Request.Body).ReadToEndAsync();

    // Use the provided prompt for chat
    string prompt = requestText;

    var responses = new List<string>();
    //ChatSession session = new ChatSession(ex);
    foreach (var text in session.Chat(prompt, new InferenceParams { Temperature = 0.6f, AntiPrompts = new List<string> { "User:" } }))
    {
        responses.Add(text);
    }
    var ans = string.Join("|" , responses);

    await httpContext.Response.WriteAsJsonAsync(ans);
});


app.Run();
