using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Module = Autofac.Module;
using System.Reflection;
using Autofac;

namespace Consultas.Ejecutador.Infraestructura.Autofac
{
    public class ServiciosModule : Module
    {

        protected override void Load(ContainerBuilder builder)
        {

            builder.RegisterAssemblyTypes(Assembly.Load("Consultas.Servicios"))
              .Where(t => t.Name.EndsWith("Servicio") || t.Name.EndsWith("Trabajador"))
              .AsImplementedInterfaces()
              .InstancePerLifetimeScope();


        }
    }
}
