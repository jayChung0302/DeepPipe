using System;
using System.Collections.Generic;
using System.Text;

namespace DpDb
{
    public class Defect
    {
        public Guid DefectId { get; set; }
        public Guid PipeTaskId { get; set; }
        public double Timestamp { get; set; }
        public string DefectName { get; set; }
        public int Index { get; set; }
        public byte[] Image { get; set; }
    }
}
