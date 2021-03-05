using Consultas.Datos.Daos.Abstracciones;
using Consultas.Datos.Entidades;
using Consultas.Servicios.Consultas.Sunedu.Dtos;
using Consultas.Servicios.Consultas.Sunedu.Servicios.Abstracciones;
using Consultas.Servicios.Consultas.Sunedu.Trabajadores.Abstracciones;
using Consultas.Servicios.Infraestructura.Dtos;
using Hangfire;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Consultas.Servicios.Consultas.Sunedu.Trabajadores.Implementaciones
{
    public class SuneduTrabajador : ISuneduTrabajador
    {
        private readonly ISuneduServicio _suneduServicio;
        private readonly ISuneduDniColaDao _suneduDniColaDao;
        private readonly ITituloAcademicoDao _tituloAcademicoDao;
        private readonly SuneduConfiguracionDto _suneduConfiguracion;

        public SuneduTrabajador(
            SuneduConfiguracionDto suneduConfiguracion,
            ISuneduServicio suneduServicio,
            ISuneduDniColaDao suneduDniColaDao,
            ITituloAcademicoDao tituloAcademicoDao
            )
        {
            _suneduDniColaDao = suneduDniColaDao;
            _suneduServicio = suneduServicio;
            _tituloAcademicoDao = tituloAcademicoDao;
            _suneduConfiguracion = suneduConfiguracion;
        }

        public async Task RealizarTrabajo(IJobCancellationToken cancellationToken)
        {

            while (true)
            {
                var hora = DateTime.Now.Hour;
                var delay = 30000;

                if (hora >= 6 && hora < 23)
                {
                    delay = 10000;
                }

                try
                {
                    await RealizarScraping();
                }
                catch { }

                cancellationToken.ThrowIfCancellationRequested();
                await Task.Delay(delay);
            }

        }


        private async Task RealizarScraping()
        {
            var dni = await _suneduDniColaDao.ObtenerSiguiente();
            if (string.IsNullOrWhiteSpace(dni))
            {
                return;
            }

            var contador = 0;
            var ultimoCodigo = default(CodigosOperacionDto);

            while (contador < 5)
            {
                ultimoCodigo = await ObteneryGuardar(dni);
                if (ultimoCodigo == CodigosOperacionDto.Suceso)
                {
                    break;
                }

                await Task.Delay(10000);
                contador++;
            }

            if (ultimoCodigo == CodigosOperacionDto.CaptchaIncorrecto)
            {
                await _suneduDniColaDao.InsertarEnCola(dni);
            }

        }

        private async Task GuardarLista(string dni, List<TituloSuneduDto> listaDto)
        {
            await _tituloAcademicoDao.EliminarPorDni(dni);

            foreach (var dto in listaDto)
            {
                var entidad = new TituloAcademico()
                {
                    Dni = dni,
                    Fecha = dto.FechaDiploma,
                    Institucion = dto.Institucion,
                    Titulo = dto.Titulo
                };

                await _tituloAcademicoDao.Insertar(entidad);
            }
        }

        private async Task<CodigosOperacionDto> ObteneryGuardar(string dni)
        {

            var operacion = await _suneduServicio.ListarTitulos(new PeticionTituloSuneduDto()
            {
                Dni = dni,
                RutaFolderTrabajo = _suneduConfiguracion.RutaFolderTrabajo,
                RutaTesseract = _suneduConfiguracion.RutaTesseract,
                UrlSunedu = _suneduConfiguracion.UrlSunedu,
                UserAgent = _suneduConfiguracion.UserAgent
            });

            if (operacion.Completado)
            {
                await GuardarLista(dni, operacion.Resultado);
            }

            return operacion.Codigo;
        }
    }
}
