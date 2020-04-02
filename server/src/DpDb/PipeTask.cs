using System;
using System.Collections.Generic;
using System.Text;

namespace DpDb
{
    public class PipeTask
    {
        public Guid PipeTaskId { get; set; }
        public DateTime Registered { get; set; }
        public string VideoMD5 { get; set; }
        #region relation
        public ICollection<Defect> Defects { get; set; }
        #endregion
    }
}
