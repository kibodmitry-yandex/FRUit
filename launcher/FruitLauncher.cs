// FRUit — тонкий exe-лаунчер (как MyBL.exe): не содержит кода утилиты, а на
// каждом запуске зовёт ТЕКУЩИЙ пакет fruit питоном окружения.
//
// Собран как WINDOWLESS-приложение (/target:winexe): окна терминала НЕТ.
//   * без аргументов (или «tray») — тихий запуск трея: pythonw.exe, весь
//     stdout/stderr утилиты дописывается в logs\fruit.log;
//   * с аргументами (save/restore/list/…) — выделяется консоль, чтобы видеть
//     вывод CLI-команды.
//
// Переопределения: FRUIT_HOME (каталог с пакетом fruit), FRUIT_PYTHON (python).
using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;

internal static class FruitLauncher
{
    private static string _log;

    [DllImport("kernel32.dll")]
    private static extern bool AllocConsole();

    private static int Main(string[] args)
    {
        string home = FindHome();
        string logdir = Path.Combine(home ?? BaseDir(), "logs");
        try { Directory.CreateDirectory(logdir); } catch { /* ignore */ }
        _log = Path.Combine(logdir, "fruit.log");
        Rotate();

        bool hidden = args == null || args.Length == 0
            || (args.Length == 1 && string.Equals(args[0], "tray", StringComparison.OrdinalIgnoreCase));

        if (!hidden)
        {
            AllocConsole();
            try { Console.OutputEncoding = new UTF8Encoding(false); } catch { /* ignore */ }
            Console.Title = "FRUit";
        }

        try
        {
            if (home == null)
            {
                Report(hidden, "Не найден пакет fruit (каталог с fruit\\__main__.py). " +
                               "Положи лаунчер в корень FRUit или задай FRUIT_HOME.");
                return 2;
            }
            string py = FindPython(home, hidden);
            if (py == null)
            {
                Report(hidden, "Не найден python.exe. Задай FRUIT_PYTHON=путь\\к\\python.exe");
                return 3;
            }

            // -u: pythonw без консоли буферизует stdout блоками и без -u лог пуст,
            //     пока процесс (трей) не завершится.
            string argline = "-u -X utf8 -m fruit " + JoinArgs(args);
            string inner = Quote(py) + " " + argline;
            if (hidden)
                inner += " >> " + Quote(_log) + " 2>&1";   // весь вывод — в лог

            var psi = new ProcessStartInfo
            {
                FileName = "cmd.exe",
                Arguments = "/c \"" + inner + "\"",
                WorkingDirectory = home,
                UseShellExecute = false,
                CreateNoWindow = hidden,
                WindowStyle = hidden ? ProcessWindowStyle.Hidden : ProcessWindowStyle.Normal,
            };
            psi.EnvironmentVariables["FRUIT_LAUNCHER"] = "1";
            psi.EnvironmentVariables["PYTHONUTF8"] = "1";
            psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";

            Log(string.Format("запуск: {0} {1} (cwd={2})", py, argline, home));
            Process p = Process.Start(psi);

            if (hidden)
            {
                // тихий режим: не ждём, не держим лишний процесс — пусть трей живёт сам
                return 0;
            }

            p.WaitForExit();
            Console.WriteLine();
            Console.WriteLine("[FRUit] код {0}", p.ExitCode);
            if (p.ExitCode != 0)
            {
                Console.WriteLine("[FRUit] Enter — закрыть окно.");
                Console.ReadLine();
            }
            return p.ExitCode;
        }
        catch (Exception e)
        {
            Report(hidden, "КРИТИЧЕСКАЯ ОШИБКА: " + e);
            return 1;
        }
    }

    private static string JoinArgs(string[] args)
    {
        if (args == null || args.Length == 0) return "tray";
        var sb = new StringBuilder();
        foreach (string a in args)
        {
            if (sb.Length > 0) sb.Append(' ');
            sb.Append(a.IndexOf(' ') >= 0 ? Quote(a) : a);
        }
        return sb.ToString();
    }

    private static string Quote(string s) { return "\"" + s + "\""; }

    private static string BaseDir()
    {
        return AppDomain.CurrentDomain.BaseDirectory.TrimEnd(
            Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
    }

    // Каталог, где лежит пакет fruit (есть fruit\__main__.py).
    private static string FindHome()
    {
        string env = Environment.GetEnvironmentVariable("FRUIT_HOME");
        if (!string.IsNullOrEmpty(env) && HasPackage(env)) return env;

        string d = BaseDir();
        for (int i = 0; i < 6 && !string.IsNullOrEmpty(d); i++)
        {
            if (HasPackage(d)) return d;
            DirectoryInfo p = Directory.GetParent(d);
            d = (p == null) ? null : p.FullName;
        }
        string fb = @"F:\FRUit";
        if (HasPackage(fb)) return fb;
        return null;
    }

    private static bool HasPackage(string dir)
    {
        return File.Exists(Path.Combine(Path.Combine(dir, "fruit"), "__main__.py"));
    }

    // hidden → pythonw.exe (без окна), иначе python.exe (с консолью).
    private static string FindPython(string home, bool hidden)
    {
        string env = Environment.GetEnvironmentVariable("FRUIT_PYTHON");
        if (!string.IsNullOrEmpty(env) && File.Exists(env)) return env;
        string[] names = hidden
            ? new[] { "pythonw.exe", "python.exe" }
            : new[] { "python.exe", "pythonw.exe" };
        foreach (string exe in names)
        {
            string p = Path.Combine(Path.Combine(
                Path.Combine(home, ".venv"), "Scripts"), exe);
            if (File.Exists(p)) return p;
        }
        return hidden ? "pythonw.exe" : "python.exe";
    }

    private static void Report(bool hidden, string msg)
    {
        if (hidden) Log(msg);
        else Console.WriteLine("[FRUit] " + msg);
    }

    private static void Log(string msg)
    {
        try
        {
            string line = string.Format("[{0:yyyy-MM-dd HH:mm:ss}] {1}\r\n",
                DateTime.Now, msg);
            File.AppendAllText(_log, line, new UTF8Encoding(false));
        }
        catch { /* ignore */ }
    }

    // Лог не растёт бесконечно: старше 1 МБ — в fruit.log.1
    private static void Rotate()
    {
        try
        {
            var fi = new FileInfo(_log);
            if (fi.Exists && fi.Length > 1000000)
            {
                string old = _log + ".1";
                if (File.Exists(old)) File.Delete(old);
                File.Move(_log, old);
            }
        }
        catch { /* ignore */ }
    }
}
