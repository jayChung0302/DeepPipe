using System;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;

namespace DpDb
{
    public class DpDbContext : DbContext
    {
        public DpDbContext(DbContextOptions options) : base(options) { }

        public virtual DbSet<Defect> TbDefects { get; set; }
        public virtual DbSet<PipeTask> TbPipeTask { get; set; }
        public virtual DbSet<User> TbUser { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);
            modelBuilder.Entity<Defect>(entity =>
            {
                entity.HasKey(e => e.DefectId);
                entity.Property(e => e.PipeTaskId)
                    .IsRequired(true);
                entity.Property(e => e.DefectName)
                    .IsRequired(true);
                entity.Property(e => e.Image)
                    .IsRequired(true);
            });
            modelBuilder.Entity<PipeTask>(entity =>
            {
                entity.HasKey(e => e.PipeTaskId);
                entity.HasIndex(e => e.Registered);
                entity.HasMany(e => e.Defects)
                    .WithOne()
                    .HasForeignKey(e => e.PipeTaskId)
                    .HasPrincipalKey(e => e.PipeTaskId);
            });
            modelBuilder.Entity<User>(entity =>
            {
                entity.HasKey(e => e.UserId);
                entity.Property(e => e.Password)
                    .IsRequired(true);
            });
        }
    }
}
