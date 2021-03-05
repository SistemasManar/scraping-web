using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Module = Autofac.Module;
using Autofac;
using Microsoft.Extensions.Configuration;
using Consultas.Datos.Infraestructura;
using Consultas.Servicios.Consultas.Sunedu.Dtos;

namespace Consultas.WebApi.Infraestructura.Autofac
{
    public class ConfiguracionModule : Module
    {
        private readonly IConfiguration _configuration;

        public ConfiguracionModule(IConfiguration configuration)
        {
            _configuration = configuration;
        }

        protected override void Load(ContainerBuilder builder)
        {

            builder.Register(e => new SuneduConfiguracionDto()
            {
                UrlSunedu = _configuration["sunedu:urlSunedu"],
                RutaFolderTrabajo = _configuration["sunedu:rutaFolderTrabajo"],
                RutaTesseract = _configuration["sunedu:rutaTesseract"],
                UserAgent = _configuration["sunedu:userAgent"]
            }).InstancePerLifetimeScope();

            builder.Register(e => new DatabaseConfiguracion()
            {
                CadenaConexion = _configuration.GetConnectionString("scraping")
            }).InstancePerLifetimeScope();

        }
    }
}
