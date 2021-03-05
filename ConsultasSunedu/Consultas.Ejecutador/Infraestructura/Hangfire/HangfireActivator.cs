using System;
using System.Collections.Generic;
using System.Text;
using Hangfire;

namespace Consultas.Ejecutador.Infraestructura.Hangfire
{
    public class HangfireActivator : JobActivator
    {
        private readonly IServiceProvider _serviceProvider;

        public HangfireActivator(IServiceProvider serviceProvider)
        {
            _serviceProvider = serviceProvider;
        }

        public override object ActivateJob(Type type)
        {
            return _serviceProvider.GetService(type);
        }
    }
}
