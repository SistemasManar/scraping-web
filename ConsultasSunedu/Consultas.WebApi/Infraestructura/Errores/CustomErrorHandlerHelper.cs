using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Hosting;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Threading.Tasks;

namespace Consultas.WebApi.Infraestructura.Errores
{
    public static class CustomErrorHandlerHelper
    {
        public static void UseCustomErrors(this IApplicationBuilder app, IHostEnvironment environment)
        {
            if (environment.IsDevelopment())
            {
                app.Use(WriteDevelopmentResponse);
            }
            else
            {
                app.Use(WriteProductionResponse);
            }
        }

        private static Task WriteDevelopmentResponse(HttpContext httpContext, Func<Task> next)
        => WriteResponse(httpContext, includeDetails: true);

        private static Task WriteProductionResponse(HttpContext httpContext, Func<Task> next)
            => WriteResponse(httpContext, includeDetails: false);

        private static async Task WriteResponse(HttpContext context, bool includeDetails)
        {

            var exceptionHandlerPathFeature =
                                context.Features.Get<IExceptionHandlerPathFeature>();

            var errorGeneral = exceptionHandlerPathFeature?.Error;

            if (errorGeneral == null)
            {
                return;
            }

            if (errorGeneral is ApiError error)
            {
                context.Response.StatusCode = (int)error.HttpCode;
                context.Response.ContentType = "application/json";
                var result = JsonConvert.SerializeObject(new { codigo = error.CodigoError, mensajes = error.Errores });
                await context.Response.WriteAsync(result);
                return;
            }


            var title = includeDetails ? "Ocurrio un error: " + errorGeneral.Message : "Ocurrio un error";
            var details = includeDetails ? errorGeneral.ToString() : null;



            context.Response.StatusCode = (int)HttpStatusCode.InternalServerError;
            context.Response.ContentType = "application/json";
            await context.Response.WriteAsync(JsonConvert.SerializeObject(new { error = title, detalle = details }));

        }
    }
}
