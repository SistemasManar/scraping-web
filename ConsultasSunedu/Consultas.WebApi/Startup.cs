using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Autofac;
using Autofac.Extensions.DependencyInjection;
using Consultas.WebApi.Infraestructura.Autofac;
using Consultas.WebApi.Infraestructura.Errores;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Hangfire;
using Hangfire.SqlServer;


namespace Consultas.WebApi
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            services.AddControllers().AddNewtonsoftJson();
            services.AddAutofac();

            services.AddHangfire(config =>
            {
                config.UseSqlServerStorage(Configuration.GetConnectionString("hangfire"));
            });

        }

        public void ConfigureContainer(ContainerBuilder builder)
        {

            builder.RegisterModule(new ConfiguracionModule(Configuration));
            builder.RegisterModule(new DatosModule());
            builder.RegisterModule(new ServiciosModule());
            // Add things to the Autofac ContainerBuilder.
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }

            app.UseRouting();

            app.UseExceptionHandler(errorApp => errorApp.UseCustomErrors(env));

            app.UseHangfireDashboard();

            app.UseAuthorization();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers();
            });
        }
    }
}
