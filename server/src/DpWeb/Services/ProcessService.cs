using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using DpDb;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace DpWeb.Services
{
    public class ProcessService
    {
        private readonly IServiceProvider serviceProvider = null;
        private readonly IConfiguration configuration = null;
        private readonly ILogger logger = null;
        private readonly string appRoot = Path.GetDirectoryName(Assembly.GetEntryAssembly().Location);
        private readonly Dictionary<Guid, Task> map = new Dictionary<Guid, Task>();

        public ProcessService(IServiceProvider serviceProvider, IConfiguration configuration, ILogger<ProcessService> logger)
        {
            this.serviceProvider = serviceProvider;
            this.configuration = configuration;
            this.logger = logger;
        }

        public void Invoke(Guid pipeTaskId, string videoFullPath)
        {
            logger.LogTrace("Invoke {@}", new { pipeTaskId, videoFullPath });
            map.Add(pipeTaskId, Task.Run(async () =>
            {
                try
                {
                    string outputFullPath = Path.Combine(appRoot, pipeTaskId.ToString());
                    Directory.CreateDirectory(outputFullPath);
                    var startInfo = new ProcessStartInfo
                    {
                        FileName = configuration["DeepPipe:Python"],
                        Arguments = $" {configuration["DeepPipe:Command"]}" +
                                    $" --video_dir {videoFullPath}" +
                                    $" --output_dir {outputFullPath}/",
                    };
                    logger.LogInformation("Try run process {@}", new { startInfo.FileName, startInfo.Arguments, });
                    var process = Process.Start(startInfo);
                    process.WaitForExit();

                    if (process.ExitCode != 0)
                    {
                        throw new InvalidOperationException("ExitCode not zero");
                    }

                    var lines = await File.ReadAllLinesAsync(
                        Path.Combine(outputFullPath, "defects.txt"),
                        Encoding.UTF8);

                    var defects = lines.Skip(1)
                        .Select(line =>
                        {
                            var row = line.Split(',').Select(e => e.Trim()).ToArray();
                            return new Defect
                            {
                                DefectId = Guid.NewGuid(),
                                PipeTaskId = pipeTaskId,
                                Timestamp = double.Parse(row[0]),
                                DefectName = row[1],
                                Index = int.Parse(row[2]),
                                Image = File.ReadAllBytes(Path.Combine(outputFullPath, $"{row[1]}{row[2]}.png")),
                            };
                        })
                        .ToArray();

                    using (var context = serviceProvider.GetRequiredService<DpDbContext>())
                    {
                        await context.TbDefects.AddRangeAsync(defects);
                        await context.SaveChangesAsync();
                    }
                }
                catch (Exception e)
                {
                    logger.LogError(e, "Invoke fail {@}", new { pipeTaskId, videoFullPath });
                    throw e;
                }
            }));
        }

        public bool TrtGetStatus(Guid pipeTaskId, out TaskStatus status)
        {
            if (map.TryGetValue(pipeTaskId, out var task))
            {
                status = task.Status;
                return true;
            }
            else
            {
                status = default;
                return false;
            }
        }
    }
}
