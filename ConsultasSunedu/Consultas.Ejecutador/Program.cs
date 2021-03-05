using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Autofac;
using Autofac.Extensions.DependencyInjection;
using Consultas.Ejecutador.Infraestructura.Autofac;
using Consultas.Ejecutador.Infraestructura.Hangfire;
using Hangfire;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

namespace Consultas.Ejecutador
{
    public class Program
    {
        public static void Main(string[] args)
        {
            CreateHostBuilder(args).Build().Run();
        }

        public static IHostBuilder CreateHostBuilder(string[] args) =>
            Host.CreateDefaultBuilder(args)
                .UseServiceProviderFactory(new AutofacServiceProviderFactory())
                 .ConfigureContainer<ContainerBuilder>((hostContext, builder) =>
                 {
                     builder.RegisterModule(new ConfiguracionModule(hostContext.Configuration));
                     builder.RegisterModule(new DatosModule());
                     builder.RegisterModule(new ServiciosModule());

                 })
                .ConfigureServices((hostContext, services) =>
                {

                    GlobalConfiguration.Configuration.UseActivator(new HangfireActivator(services.BuildServiceProvider()));


                    services.AddHangfire(config =>
                    {
                        config.UseSqlServerStorage(hostContext.Configuration.GetConnectionString("hangfire"));
                    });


                    if (hostContext.Configuration["colas:sunedu"].Equals("1", StringComparison.OrdinalIgnoreCase))
                    {
                        services.AddHangfireServer(options =>
                        {
                            options.Queues = new[] { "scraping_sunedu" };
                            options.WorkerCount = 1;
                        });

                    }


                    if (hostContext.Configuration["colas:sunat"].Equals("1", StringComparison.OrdinalIgnoreCase))
                    {
                        services.AddHangfireServer(options =>
                        {
                            options.Queues = new[] { "scraping_sunat_empresa" };
                            options.WorkerCount = 1;
                        });

                    }


                    if (hostContext.Configuration["colas:soat"].Equals("1", StringComparison.OrdinalIgnoreCase))
                    {
                        services.AddHangfireServer(options =>
                        {
                            options.Queues = new[] { "scraping_apeseg_soat" };
                            options.WorkerCount = 1;
                        });

                    }


                    services.AddHostedService<Worker>();
                })
            .UseWindowsService()
            ;
    }
}
