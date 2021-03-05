using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Module = Autofac.Module;
using System.Reflection;
using Autofac;

namespace Consultas.Ejecutador.Infraestructura.Autofac
{
    public class DatosModule: Module
    {
        protected override void Load(ContainerBuilder builder)
        {
            builder.RegisterAssemblyTypes(Assembly.Load("Consultas.Datos"))
              .Where(t => t.Name.EndsWith("Dao"))
              .AsImplementedInterfaces()
              .InstancePerLifetimeScope();

        }
    }
}
