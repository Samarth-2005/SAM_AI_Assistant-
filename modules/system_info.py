import psutil
import platform
import json
import os

resource_history = []
RESOURCE_HISTORY_FILE = os.path.join(
    os.path.dirname(__file__),
    "resource_history.json"
)

def get_system_info():

    try:

        # Operating system
        system = platform.system()
        release = platform.release()

        # CPU usage
        cpu = psutil.cpu_percent(interval=1)

        # RAM usage
        memory = psutil.virtual_memory()
        ram = memory.percent

        # Disk usage
        disk = psutil.disk_usage("C:\\")
        disk_percent = disk.percent

        # CPU core information
        physical_cores = psutil.cpu_count(logical=False)
        logical_cores = psutil.cpu_count(logical=True)

        # Battery information
        battery = psutil.sensors_battery()

        if battery:

            battery_percent = battery.percent

            if battery.power_plugged:
                power_status = "plugged in"
            else:
                power_status = "running on battery"

        else:

            battery_percent = "unknown"
            power_status = "unknown"

        return (
            f"Your computer is running {system} {release}. "
            f"CPU usage is {cpu} percent. "
            f"Memory usage is {ram} percent. "
            f"Disk usage is {disk_percent} percent. "
            f"Your computer has {physical_cores} physical CPU cores "
            f"and {logical_cores} logical CPU cores. "
            f"Battery is at {battery_percent} percent "
            f"and the laptop is {power_status}."
        )

    except Exception as e:

        print("System Information Error:", e)

        return "Sorry, I couldn't get the system information."
def get_short_system_info():

    try:

        cpu = psutil.cpu_percent(interval=1)

        ram = psutil.virtual_memory().percent

        disk = psutil.disk_usage("C:\\").percent

        battery = psutil.sensors_battery()

        if battery:
            battery_percent = battery.percent
        else:
            battery_percent = "unknown"

        return (
            f"CPU is at {cpu} percent. "
            f"RAM is at {ram} percent. "
            f"Disk usage is {disk} percent. "
            f"Battery is at {battery_percent} percent."
        )

    except Exception as e:

        print("Short System Information Error:", e)

        return "Sorry, I couldn't get the quick system status."
def get_system_health():

    try:

        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:\\").percent

        battery = psutil.sensors_battery()

        if battery:
            battery_percent = battery.percent
        else:
            battery_percent = None

        warnings = []

        # CPU
        if cpu >= 90:
            warnings.append("CPU usage is critical")
        elif cpu >= 80:
            warnings.append("CPU usage is high")

        # RAM
        if ram >= 90:
            warnings.append("memory usage is critical")
        elif ram >= 80:
            warnings.append("memory usage is high")

        # Disk
        if disk >= 95:
            warnings.append("disk space is critically low")
        elif disk >= 90:
            warnings.append("disk space is getting low")

        # Battery
        if battery_percent is not None:
            if battery_percent <= 10:
                warnings.append("battery is critically low")
            elif battery_percent <= 20:
                warnings.append("battery is low")

        # Determine overall status
        critical = any("critical" in warning for warning in warnings)

        if critical:

            status = "Critical"

        elif warnings:

            status = "Needs attention"

        else:

            status = "Healthy"

        # Final response
        if warnings:

            return (
                f"System status is {status}. "
                + ". ".join(warnings)
                + ". "
                f"CPU is {cpu} percent, "
                f"memory is {ram} percent, "
                f"disk usage is {disk} percent"
                + (
                    f", and battery is {battery_percent} percent."
                    if battery_percent is not None
                    else "."
                )
            )

        return (
            f"System status is {status}. "
            f"CPU is {cpu} percent, "
            f"memory is {ram} percent, "
            f"disk usage is {disk} percent"
            + (
                f", and battery is {battery_percent} percent."
                if battery_percent is not None
                else "."
            )
        )

    except Exception as e:

        print("System Health Error:", e)

        return "Sorry, I couldn't check your system health."
def get_running_processes():

    try:

        processes = []

        for process in psutil.process_iter(
            ["pid", "name"]
        ):

            try:

                pid = process.info["pid"]
                name = process.info["name"]

                if name:

                    processes.append(
                        f"{name} (PID {pid})"
                    )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):

                continue

        return processes

    except Exception as e:

        print("Process Error:", e)

        return []
def get_top_cpu_processes(limit=5):

    try:

        processes = []

        # First measurement
        for process in psutil.process_iter(
            ["pid", "name"]
        ):

            try:

                process.cpu_percent(None)

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):

                continue

        # Give Windows a moment to measure CPU usage
        import time
        time.sleep(1)

        # Second measurement
        for process in psutil.process_iter(
            ["pid", "name"]
        ):

            try:

                name = process.info["name"]

                # Ignore Windows idle process
                if not name:
                    continue

                if name.lower() == "system idle process":
                    continue

                cpu = process.cpu_percent(None)

                processes.append({
                    "pid": process.info["pid"],
                    "name": name,
                    "cpu": cpu
                })

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):

                continue

        processes.sort(
            key=lambda x: x["cpu"],
            reverse=True
        )

        return processes[:limit]

    except Exception as e:

        print("CPU Process Error:", e)

        return []
def get_top_memory_processes(limit=5):

    try:

        processes = []

        for process in psutil.process_iter(
            ["pid", "name", "memory_percent"]
        ):

            try:

                memory = process.info["memory_percent"]

                if memory is None:
                    memory = 0.0

                processes.append({
                    "pid": process.info["pid"],
                    "name": process.info["name"],
                    "memory": memory
                })

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):

                continue

        processes.sort(
            key=lambda x: x["memory"],
            reverse=True
        )

        return processes[:limit]

    except Exception as e:

        print("Memory Process Error:", e)

        return []
def close_application(app_name):

    try:

        app_name = app_name.lower().strip()

        # =================================================
        # PROTECTED WINDOWS PROCESSES
        # =================================================

        protected_processes = {
            "system",
            "system idle process",
            "registry",
            "smss.exe",
            "csrss.exe",
            "wininit.exe",
            "winlogon.exe",
            "services.exe",
            "lsass.exe",
            "lsaiso.exe"
        }

        # =================================================
        # CHECK IF USER IS TRYING TO CLOSE A PROTECTED
        # PROCESS
        # =================================================

        if app_name in protected_processes:

            print(
                f"Blocked attempt to close "
                f"protected process: {app_name}"
            )

            return (
                f"I cannot close {app_name} "
                f"because it is an important "
                f"Windows system process."
            )

        closed = False

        # =================================================
        # FIND AND CLOSE APPLICATION
        # =================================================

        for process in psutil.process_iter(
            ["pid", "name"]
        ):

            try:

                name = process.info["name"]

                if not name:
                    continue

                process_name = name.lower()

                # Don't close protected processes
                if process_name in protected_processes:
                    continue

                if app_name in process_name:

                    print(
                        f"Closing {name} "
                        f"(PID {process.info['pid']})"
                    )

                    process.terminate()

                    closed = True

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):

                continue

        if closed:

            return f"I closed {app_name}."

        return (
            f"I couldn't find {app_name} "
            f"running."
        )

    except Exception as e:

        print(
            "Close Application Error:",
            e
        )

        return (
            "Sorry, I couldn't close "
            "that application."
        )
# =====================================================
# CPU HEALTH CHECK
# =====================================================

def get_cpu_health():

    try:

        cpu = psutil.cpu_percent(interval=1)

        if cpu >= 90:

            return (
                f"CPU usage is {cpu:.1f} percent. "
                "CPU usage is critical."
            )

        elif cpu >= 80:

            return (
                f"CPU usage is {cpu:.1f} percent. "
                "CPU usage is high."
            )

        elif cpu >= 60:

            return (
                f"CPU usage is {cpu:.1f} percent. "
                "CPU usage is moderately high."
            )

        else:

            return (
                f"CPU usage is {cpu:.1f} percent. "
                "CPU usage is normal."
            )

    except Exception as e:

        print(
            "CPU Health Error:",
            e
        )

        return (
            "Sorry, I couldn't check CPU health."
        )
# =====================================================
# RAM HEALTH CHECK
# =====================================================

def get_ram_health():

    try:

        ram = psutil.virtual_memory().percent

        if ram >= 90:

            return (
                f"Memory usage is {ram:.1f} percent. "
                "Memory usage is critical."
            )

        elif ram >= 80:

            return (
                f"Memory usage is {ram:.1f} percent. "
                "Memory usage is high."
            )

        elif ram >= 60:

            return (
                f"Memory usage is {ram:.1f} percent. "
                "Memory usage is moderately high."
            )

        else:

            return (
                f"Memory usage is {ram:.1f} percent. "
                "Memory usage is normal."
            )

    except Exception as e:

        print(
            "RAM Health Error:",
            e
        )

        return (
            "Sorry, I couldn't check memory health."
        )
# =====================================================
# DISK HEALTH CHECK
# =====================================================

def get_disk_health():

    try:

        disk = psutil.disk_usage("C:\\")
        usage = disk.percent

        if usage >= 95:

            return (
                f"Disk usage is {usage:.1f} percent. "
                "Your disk space is critically low."
            )

        elif usage >= 85:

            return (
                f"Disk usage is {usage:.1f} percent. "
                "Your disk space is getting low."
            )

        elif usage >= 70:

            return (
                f"Disk usage is {usage:.1f} percent. "
                "Disk usage is moderately high."
            )

        else:

            return (
                f"Disk usage is {usage:.1f} percent. "
                "Your disk space is healthy."
            )

    except Exception as e:

        print(
            "Disk Health Error:",
            e
        )

        return (
            "Sorry, I couldn't check disk health."
        )
# =====================================================
# DETAILED SYSTEM HEALTH REPORT
# =====================================================

def get_detailed_system_health():

    try:

        cpu = get_cpu_health()
        ram = get_ram_health()
        disk = get_disk_health()

        battery_info = psutil.sensors_battery()

        if battery_info:

            battery = (
                f"Battery is at "
                f"{battery_info.percent:.1f} percent."
            )

        else:

            battery = "Battery information is unavailable."

        report = (
            "Here is your detailed system health report. "
            f"{cpu} "
            f"{ram} "
            f"{disk} "
            f"{battery}"
        )

        return report

    except Exception as e:

        print(
            "Detailed System Health Error:",
            e
        )

        return (
            "Sorry, I couldn't generate "
            "the detailed system health report."
        )
# =====================================================
# SLOW SYSTEM DIAGNOSIS
# =====================================================

def diagnose_slow_system():

    try:

        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:\\").percent

        problems = []

        if cpu >= 80:

            problems.append(
                f"CPU usage is high at {cpu:.1f} percent."
            )

        if ram >= 80:

            problems.append(
                f"Memory usage is high at {ram:.1f} percent."
            )

        if disk >= 90:

            problems.append(
                f"Disk usage is very high at {disk:.1f} percent."
            )

        if problems:

            diagnosis = (
                "I found possible reasons why your computer "
                "may be slow. "
                + " ".join(problems)
            )

        else:

            diagnosis = (
                "Your CPU, memory, and disk usage are currently "
                "within normal levels. I couldn't find an obvious "
                "system resource problem."
            )

        return diagnosis

    except Exception as e:

        print(
            "Slow System Diagnosis Error:",
            e
        )

        return (
            "Sorry, I couldn't diagnose why your "
            "computer may be slow."
        )
# =====================================================
# DETAILED SLOW SYSTEM DIAGNOSIS
# =====================================================

def diagnose_slow_system_detailed():

    try:

        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:\\").percent

        problems = []

        # ---------------------------------------------
        # CPU CHECK
        # ---------------------------------------------

        if cpu >= 80:

            cpu_processes = get_top_cpu_processes(1)

            if cpu_processes:

                process = cpu_processes[0]

                problems.append(
                    f"CPU usage is high at {cpu:.1f} percent. "
                    f"{process['name']} is using "
                    f"{process['cpu']:.1f} percent CPU."
                )

            else:

                problems.append(
                    f"CPU usage is high at {cpu:.1f} percent."
                )

        # ---------------------------------------------
        # RAM CHECK
        # ---------------------------------------------

        if ram >= 80:

            memory_processes = get_top_memory_processes(1)

            if memory_processes:

                process = memory_processes[0]

                problems.append(
                    f"Memory usage is high at {ram:.1f} percent. "
                    f"{process['name']} is using "
                    f"{process['memory']:.1f} percent memory."
                )

            else:

                problems.append(
                    f"Memory usage is high at {ram:.1f} percent."
                )

        # ---------------------------------------------
        # DISK CHECK
        # ---------------------------------------------

        if disk >= 90:

            problems.append(
                f"Disk usage is very high at "
                f"{disk:.1f} percent."
            )

        # ---------------------------------------------
        # FINAL DIAGNOSIS
        # ---------------------------------------------

        if problems:

            diagnosis = (
                "I found possible causes of the slowdown. "
                + " ".join(problems)
            )

        else:

            diagnosis = (
                "CPU, memory, and disk usage are currently "
                "within normal levels. I couldn't find an "
                "obvious resource problem."
            )

        return diagnosis

    except Exception as e:

        print(
            "Detailed Slow System Diagnosis Error:",
            e
        )

        return (
            "Sorry, I couldn't perform a detailed "
            "slow system diagnosis."
        )
# =====================================================
# SYSTEM SLOWDOWN RECOMMENDATIONS
# =====================================================

def get_slow_system_recommendations():

    try:

        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:\\").percent

        recommendations = []

        # ---------------------------------------------
        # CPU
        # ---------------------------------------------

        if cpu >= 80:

            cpu_processes = get_top_cpu_processes(1)

            if cpu_processes:

                process = cpu_processes[0]

                recommendations.append(
                    f"Consider closing {process['name']} "
                    f"because it is using "
                    f"{process['cpu']:.1f} percent CPU."
                )

            else:

                recommendations.append(
                    "Consider closing unnecessary applications "
                    "to reduce CPU usage."
                )

        # ---------------------------------------------
        # RAM
        # ---------------------------------------------

        if ram >= 80:

            memory_processes = get_top_memory_processes(1)

            if memory_processes:

                process = memory_processes[0]

                recommendations.append(
                    f"Consider closing {process['name']} "
                    f"because it is using "
                    f"{process['memory']:.1f} percent memory."
                )

            else:

                recommendations.append(
                    "Consider closing unused applications "
                    "to free memory."
                )

        # ---------------------------------------------
        # DISK
        # ---------------------------------------------

        if disk >= 90:

            recommendations.append(
                "Your disk is almost full. "
                "Consider removing unnecessary files "
                "or moving large files to another drive."
            )

        # ---------------------------------------------
        # NO PROBLEM
        # ---------------------------------------------

        if not recommendations:

            recommendations.append(
                "Your main system resources look normal. "
                "If the laptop still feels slow, "
                "we can check startup applications, "
                "background processes, and disk health."
            )

        return " ".join(recommendations)

    except Exception as e:

        print(
            "Recommendation Error:",
            e
        )

        return (
            "Sorry, I couldn't generate "
            "system recommendations."
        )
# =====================================================
# COMPLETE SLOW SYSTEM REPORT
# =====================================================

def get_complete_slow_system_report():

    try:

        diagnosis = diagnose_slow_system_detailed()

        recommendations = get_slow_system_recommendations()

        report = (
            f"{diagnosis} "
            f"My recommendation is: "
            f"{recommendations}"
        )

        return report

    except Exception as e:

        print(
            "Complete Slow System Report Error:",
            e
        )

        return (
            "Sorry, I couldn't generate "
            "a complete troubleshooting report."
        )
# =====================================================
# FINAL SYSTEM TROUBLESHOOTING REPORT
# =====================================================

def get_troubleshooting_report():

    try:

        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:\\").percent

        issues = []
        resource_apps = get_application_resource_usage(3)

        if cpu >= 80:
            issues.append(
                f"CPU usage is high at {cpu:.1f} percent."
            )

        if ram >= 80:
            issues.append(
                f"RAM usage is high at {ram:.1f} percent."
            )

        if disk >= 90:
            issues.append(
                f"Disk usage is very high at {disk:.1f} percent."
            )
        if resource_apps:

            top_app = resource_apps[0]

            app_name = top_app["name"].lower()

            # Applications that are generally safe
            # to close when the user is not using them.
            safe_to_close = [
                "chrome.exe",
                "msedge.exe",
                "firefox.exe",
                "notepad.exe",
                "mspaint.exe",
                "calculatorapp.exe",
                "calc.exe",
                "code.exe",
                "onedrive.exe"
            ]

            if (
                top_app["memory"] >= 5
                or top_app["cpu"] >= 10
            ):

                if app_name in safe_to_close:

                    issues.append(
                        f"{top_app['name']} is using "
                        f"{top_app['memory']:.1f} percent memory "
                        f"and {top_app['cpu']:.1f} percent CPU. "
                        f"If you are not using it, you can close "
                        f"{top_app['name']} to reduce resource usage."
                    )

                else:

                    issues.append(
                        f"{top_app['name']} is using "
                        f"{top_app['memory']:.1f} percent memory "
                        f"and {top_app['cpu']:.1f} percent CPU. "
                        f"I recommend checking whether this "
                        f"application is needed before closing it."
                    )  

        if not issues:

            return (
                "Your laptop appears to be healthy right now. "
                f"CPU usage is {cpu:.1f} percent, "
                f"memory usage is {ram:.1f} percent, "
                f"and disk usage is {disk:.1f} percent. "
                "I couldn't find an obvious resource problem."
            )

        report = (
            "I found some possible problems with your laptop. "
            + " ".join(issues)
        )

        # Top CPU process
        if cpu >= 80:

            cpu_processes = get_top_cpu_processes(1)

            if cpu_processes:

                process = cpu_processes[0]

                report += (
                    f" The process using the most CPU is "
                    f"{process['name']} at "
                    f"{process['cpu']:.1f} percent."
                )

        # Top RAM process
        if ram >= 80:

            memory_processes = get_top_memory_processes(1)

            if memory_processes:

                process = memory_processes[0]

                report += (
                    f" The process using the most memory is "
                    f"{process['name']} at "
                    f"{process['memory']:.1f} percent."
                )

        report += (
            " I recommend closing unnecessary applications "
            "and checking again."
        )

        return report

    except Exception as e:

        print(
            "Troubleshooting Report Error:",
            e
        )

        return (
            "Sorry, I couldn't generate "
            "the troubleshooting report."
        )
# =====================================================
# RUNNING USER APPLICATIONS
# =====================================================

def get_running_applications():

    try:

        applications = []

        # Windows background/system processes
        excluded_processes = {
            "System Idle Process",
            "System",
            "Registry",
            "smss.exe",
            "csrss.exe",
            "wininit.exe",
            "services.exe",
            "lsass.exe",
            "LsaIso.exe",
            "svchost.exe",
            "fontdrvhost.exe",
            "WUDFHost.exe",
            "conhost.exe",
            "dwm.exe",
            "winlogon.exe",
            "RuntimeBroker.exe",
            "SearchHost.exe",
            "StartMenuExperienceHost.exe",
            "ShellExperienceHost.exe"
        }

        for process in psutil.process_iter(
            ["pid", "name", "status"]
        ):

            try:

                name = process.info["name"]
                pid = process.info["pid"]
                status = process.info["status"]

                if not name:
                    continue

                if status != psutil.STATUS_RUNNING:
                    continue

                if name in excluded_processes:
                    continue

                applications.append(
                    {
                        "name": name,
                        "pid": pid
                    }
                )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess
            ):

                continue

        return applications

    except Exception as e:

        print(
            "Running Applications Error:",
            e
        )

        return []
# =====================================================
# APPLICATION RESOURCE INTELLIGENCE
# =====================================================

def get_application_resource_usage(limit=5):

    try:

        applications = []
        processes = []

        cpu_count = psutil.cpu_count(logical=True)

        if not cpu_count:
            cpu_count = 1

        excluded_processes = {
            "system idle process",
            "system",
            "registry",
            "smss.exe",
            "csrss.exe",
            "wininit.exe",
            "services.exe",
            "lsass.exe",
            "lsaiso.exe",
            "svchost.exe",
            "winlogon.exe",
            "fontdrvhost.exe",
            "wudfhost.exe",
            "dwm.exe"
        }

        # =================================================
        # FIRST CPU SAMPLE
        # =================================================

        for process in psutil.process_iter(
            ["pid", "name"]
        ):

            try:

                name = process.info["name"]

                if not name:
                    continue

                if name.lower() in excluded_processes:
                    continue

                process.cpu_percent(None)

                processes.append(process)

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess
            ):

                continue

        # Measure CPU over one second
        import time
        time.sleep(1)

        # =================================================
        # SECOND CPU SAMPLE
        # =================================================

        for process in processes:

            try:

                name = process.name()
                pid = process.pid

                raw_cpu = process.cpu_percent(None)

                # Normalize CPU to roughly 0 - 100%
                cpu = raw_cpu / cpu_count

                memory = process.memory_percent()

                resource_score = round(cpu + memory, 1)

                if resource_score >= 40:
                  severity = "Very High"

                elif resource_score >= 25:
                  severity = "High"

                elif resource_score >= 10:
                  severity = "Moderate"

                else:
                  severity = "Low"


                applications.append(
             {
               "name": name,
               "pid": pid,
               "cpu": round(cpu, 1),
               "memory": round(memory, 1),
               "resource_score": resource_score,
               "severity": severity
    }
)

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess
            ):

                continue

        # Sort by combined CPU + RAM
        applications.sort(
            key=lambda x: x["resource_score"],
            reverse=True
        )

        result = applications[:limit]

        # =================================================
        # AUTOMATIC RESOURCE HISTORY
        # =================================================

        try:

            snapshot = {
                "timestamp": __import__(
                    "datetime"
                ).datetime.now(),

                "applications": result
            }

            resource_history.append(snapshot)

            if len(resource_history) > 20:
                resource_history.pop(0)

            save_resource_history()

        except Exception as e:

            print(
                "Automatic Resource History Error:",
                e
            )

        return result

    except Exception as e:

        print(
            "Application Resource Usage Error:",
            e
        )

        return []
# =====================================================
# APPLICATION RESOURCE HISTORY
# =====================================================

resource_history = []


def record_application_resource_snapshot():

    try:

        applications = get_application_resource_usage(5)

        snapshot = {
            "timestamp": __import__("datetime").datetime.now(),
            "applications": applications
        }

        resource_history.append(snapshot)

        # Keep only the latest 20 snapshots
        if len(resource_history) > 20:

            resource_history.pop(0)

        return snapshot

    except Exception as e:

        print(
            "Resource History Error:",
            e
        )

        return None
# =====================================================
# RESOURCE HISTORY ANALYSIS
# =====================================================

def get_resource_history_analysis():

    try:

        if not resource_history:

            return {
                "application": None,
                "average_memory": 0,
                "average_cpu": 0,
                "snapshots": 0
            }

        app_stats = {}

        for snapshot in resource_history:

            applications = snapshot["applications"]

            for app in applications:

                name = app["name"]

                if name not in app_stats:

                    app_stats[name] = {
                        "memory": [],
                        "cpu": []
                    }

                app_stats[name]["memory"].append(
                    app["memory"]
                )

                app_stats[name]["cpu"].append(
                    app["cpu"]
                )

        if not app_stats:

            return {
                "application": None,
                "average_memory": 0,
                "average_cpu": 0,
                "snapshots": len(resource_history)
            }

        best_app = None
        best_memory = 0
        best_cpu = 0

        for name, values in app_stats.items():

            average_memory = (
                sum(values["memory"])
                / len(values["memory"])
            )

            average_cpu = (
                sum(values["cpu"])
                / len(values["cpu"])
            )

            if average_memory > best_memory:

                best_app = name
                best_memory = average_memory
                best_cpu = average_cpu

        return {
            "application": best_app,
            "average_memory": round(best_memory, 2),
            "average_cpu": round(best_cpu, 2),
            "snapshots": len(resource_history)
        }

    except Exception as e:

        print(
            "Resource History Analysis Error:",
            e
        )

        return {
            "application": None,
            "average_memory": 0,
            "average_cpu": 0,
            "snapshots": 0
        }
# =====================================================
# SAVE RESOURCE HISTORY
# =====================================================

def save_resource_history():

    try:

        serializable_history = []

        for snapshot in resource_history:

            serializable_history.append(
                {
                    "timestamp": str(snapshot["timestamp"]),
                    "applications": snapshot["applications"]
                }
            )

        with open(
            RESOURCE_HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                serializable_history,
                file,
                indent=4
            )

    except Exception as e:

        print(
            "Save Resource History Error:",
            e
        )


# =====================================================
# LOAD RESOURCE HISTORY
# =====================================================

def load_resource_history():

    global resource_history

    try:

        if not os.path.exists(
            RESOURCE_HISTORY_FILE
        ):

            return

        with open(
            RESOURCE_HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            resource_history = json.load(file)

        # Keep only latest 20
        resource_history = resource_history[-20:]

        print(
            f"Loaded {len(resource_history)} "
            f"resource history snapshots."
        )

    except Exception as e:

        print(
            "Load Resource History Error:",
            e
        )

        resource_history = []
# =====================================================
# APPLICATION RESOURCE SPIKE DETECTION
# =====================================================

def detect_resource_spike():

    try:

        # Need at least 2 snapshots
        if len(resource_history) < 2:

            return {
                "spike_detected": False,
                "application": None,
                "resource": None,
                "previous": 0,
                "current": 0,
                "increase": 0,
                "severity": "None",
                "recommendation": "Not enough history yet.",
                "message": "Not enough resource history to detect a spike."
            }

        previous_snapshot = resource_history[-2]
        current_snapshot = resource_history[-1]

        previous_apps = {
            app["name"]: app
            for app in previous_snapshot["applications"]
        }

        current_apps = current_snapshot["applications"]

        biggest_spike = None
        biggest_increase = 0

        for current_app in current_apps:

            name = current_app["name"]

            if name not in previous_apps:
                continue

            previous_app = previous_apps[name]

            previous_memory = previous_app.get("memory", 0)
            current_memory = current_app.get("memory", 0)

            previous_cpu = previous_app.get("cpu", 0)
            current_cpu = current_app.get("cpu", 0)

            memory_increase = current_memory - previous_memory
            cpu_increase = current_cpu - previous_cpu

            # =================================================
            # MEMORY SPIKE
            # =================================================

            if (
                memory_increase >= 5
                and memory_increase > biggest_increase
            ):

                biggest_increase = memory_increase

                if memory_increase >= 20:
                    severity = "Critical"

                elif memory_increase >= 15:
                    severity = "High"

                elif memory_increase >= 10:
                    severity = "Moderate"

                else:
                    severity = "Small"

                biggest_spike = {
                    "spike_detected": True,
                    "application": name,
                    "resource": "memory",
                    "previous": round(previous_memory, 1),
                    "current": round(current_memory, 1),
                    "increase": round(memory_increase, 1),
                    "severity": severity
                }

            # =================================================
            # CPU SPIKE
            # =================================================

            if (
                cpu_increase >= 10
                and cpu_increase > biggest_increase
            ):

                biggest_increase = cpu_increase

                if cpu_increase >= 40:
                    severity = "Critical"

                elif cpu_increase >= 30:
                    severity = "High"

                elif cpu_increase >= 20:
                    severity = "Moderate"

                else:
                    severity = "Small"

                biggest_spike = {
                    "spike_detected": True,
                    "application": name,
                    "resource": "CPU",
                    "previous": round(previous_cpu, 1),
                    "current": round(current_cpu, 1),
                    "increase": round(cpu_increase, 1),
                    "severity": severity
                }

        # =====================================================
        # SPIKE FOUND
        # =====================================================

        if biggest_spike:

            severity = biggest_spike["severity"]
            app_name = biggest_spike["application"]
            resource = biggest_spike["resource"]

            if severity == "Critical":

                recommendation = (
                    f"This is a critical spike. "
                    f"{app_name} may be significantly affecting "
                    f"system performance. Check the application immediately."
                )

            elif severity == "High":

                recommendation = (
                    f"This is a high resource spike. "
                    f"If you are not actively using {app_name}, "
                    f"consider closing it."
                )

            elif severity == "Moderate":

                recommendation = (
                    f"This is a moderate resource spike. "
                    f"Monitor {app_name} and close it if "
                    f"the high usage continues."
                )

            else:

                recommendation = (
                    f"This is a small resource spike. "
                    f"No immediate action is required, "
                    f"but keep an eye on {app_name}."
                )

            biggest_spike["recommendation"] = recommendation

            biggest_spike["message"] = (
                f"{app_name} has a "
                f"{severity} {resource} usage spike. "
                f"Usage increased from "
                f"{biggest_spike['previous']:.1f} percent to "
                f"{biggest_spike['current']:.1f} percent. "
                f"{recommendation}"
            )

            return biggest_spike

        # =====================================================
        # NO SPIKE
        # =====================================================

        return {
            "spike_detected": False,
            "application": None,
            "resource": None,
            "previous": 0,
            "current": 0,
            "increase": 0,
            "severity": "None",
            "recommendation": "No action is required.",
            "message": "No significant resource spike detected."
        }

    except Exception as e:

        print(
            "Resource Spike Detection Error:",
            e
        )

        return {
            "spike_detected": False,
            "application": None,
            "resource": None,
            "previous": 0,
            "current": 0,
            "increase": 0,
            "severity": "Unknown",
            "recommendation": "Unable to generate a recommendation.",
            "message": "Unable to check for resource spikes."
        }
# =====================================================
# APPLICATION RESOURCE SUMMARY
# =====================================================

def get_application_resource_summary():

    try:

        applications = get_application_resource_usage(5)

        if not applications:

            return {
                "application": None,
                "cpu": 0,
                "memory": 0,
                "resource_score": 0,
                "severity": "Unknown"
            }

        top = applications[0]

        return {
            "application": top["name"],
            "cpu": top["cpu"],
            "memory": top["memory"],
            "resource_score": top["resource_score"],
            "severity": top["severity"]
        }

    except Exception as e:

        print(
            "Application Resource Summary Error:",
            e
        )

        return {
            "application": None,
            "cpu": 0,
            "memory": 0,
            "resource_score": 0,
            "severity": "Unknown"
        }
# =====================================================
# REPEATED RESOURCE SPIKE DETECTION
# =====================================================

def detect_repeated_resource_spikes():

    try:

        # We need several snapshots for useful comparison
        if len(resource_history) < 3:

            return {
                "repeated_spike": False,
                "application": None,
                "resource": None,
                "spike_count": 0,
                "message": "Not enough resource history to check repeated spikes."
            }

        spike_counts = {}

        # Compare every neighboring pair of snapshots
        for i in range(1, len(resource_history)):

            previous_snapshot = resource_history[i - 1]
            current_snapshot = resource_history[i]

            previous_apps = {
                app["name"]: app
                for app in previous_snapshot["applications"]
            }

            for current_app in current_snapshot["applications"]:

                name = current_app["name"]

                if name not in previous_apps:
                    continue

                previous_app = previous_apps[name]

                previous_cpu = previous_app.get("cpu", 0)
                current_cpu = current_app.get("cpu", 0)

                previous_memory = previous_app.get("memory", 0)
                current_memory = current_app.get("memory", 0)

                cpu_increase = current_cpu - previous_cpu
                memory_increase = current_memory - previous_memory
                # CPU spike = increase of at least 10%
                if cpu_increase >= 10:
                    key = (name, "CPU")
                    spike_counts[key] = (
                        spike_counts.get(key, 0) + 1
                    )
                # Memory spike = increase of at least 5%
                if memory_increase >= 5:
                    key = (name, "memory")
                    spike_counts[key] = (
                        spike_counts.get(key, 0) + 1
                    )
        if not spike_counts:
            return {
                "repeated_spike": False,
                "application": None,
                "resource": None,
                "spike_count": 0,
                "message": "No repeated resource spikes were detected."
            }
        # Find application/resource with most spikes
        top_spike = max(
            spike_counts,
            key=spike_counts.get
        )
        app_name, resource = top_spike
        spike_count = spike_counts[top_spike]
        # Require at least 2 spikes to call it repeated
        if spike_count >= 2:
            # =============================================
            # REPEATED SPIKE RECOMMENDATION
            # =============================================
            if spike_count >= 6:
                severity = "Critical"
                recommendation = (
                    f"{app_name} has repeatedly shown "
                    f"{resource} spikes. "
                    f"This may be seriously affecting system performance. "
                    f"Investigate the application and close it "
                    f"if it is not needed."
                )
            elif spike_count >= 4:
                severity = "High"
                recommendation = (
                    f"{app_name} appears to have a recurring "
                    f"{resource} usage problem. "
                    f"Consider restarting or closing the application "
                    f"if you are not using it."
                )
            else:
                severity = "Moderate"

                recommendation = (
                    f"{app_name} has shown multiple {resource} spikes. "
                    f"Monitor the application to see if the problem continues."
                )
            return {
                "repeated_spike": True,
                "application": app_name,
                "resource": resource,
                "spike_count": spike_count,
                "severity": severity,
                "recommendation": recommendation,
                "message": (
                    f"{app_name} has shown {resource} spikes "
                    f"{spike_count} times recently. "
                    f"The repeated spike severity is {severity}. "
                    f"{recommendation}"
                )
            }
            return {
            "repeated_spike": False,
            "application": app_name,
            "resource": resource,
            "spike_count": spike_count,
            "severity": "Low",
            "recommendation": (
                "This currently appears to be a temporary spike. "
                "No immediate action is required."
            ),
            "message": (
                f"I detected one {resource} spike from "
                f"{app_name}, but it is not a repeated problem yet."
            )
        }
    except Exception as e:
        print(
            "Repeated Resource Spike Error:",
            e
        )
        return {
            "repeated_spike": False,
            "application": None,
            "resource": None,
            "spike_count": 0,
            "message": "Unable to analyze repeated resource spikes."
        }
# =====================================================
# APPLICATION RESOURCE TREND DETECTION
# =====================================================

def detect_resource_trend():

    try:

        # Need at least 3 snapshots to identify a trend
        if len(resource_history) < 3:

            return {
                "trend_detected": False,
                "application": None,
                "resource": None,
                "start": 0,
                "current": 0,
                "increase": 0,
                "samples": len(resource_history),
                "message": (
                    "Not enough resource history "
                    "to detect a trend."
                )
            }

        # Use the latest 5 snapshots
        recent_history = resource_history[-5:]

        app_history = {}

        # Collect CPU and memory readings
        for snapshot in recent_history:

            for app in snapshot["applications"]:

                name = app["name"]

                if name not in app_history:

                    app_history[name] = {
                        "cpu": [],
                        "memory": []
                    }

                app_history[name]["cpu"].append(
                    app.get("cpu", 0)
                )

                app_history[name]["memory"].append(
                    app.get("memory", 0)
                )

        best_trend = None
        biggest_increase = 0

        for name, values in app_history.items():

            # We want the app to appear in at least 3 snapshots
            if len(values["cpu"]) < 3:
                continue

            # =============================================
            # CPU TREND
            # =============================================

            cpu_values = values["cpu"]

            cpu_increasing = all(
                cpu_values[i] <= cpu_values[i + 1]
                for i in range(len(cpu_values) - 1)
            )

            cpu_increase = (
                cpu_values[-1] - cpu_values[0]
            )

            if (
                cpu_increasing
                and cpu_increase >= 5
                and cpu_increase > biggest_increase
            ):

                biggest_increase = cpu_increase

                best_trend = {
                    "trend_detected": True,
                    "application": name,
                    "resource": "CPU",
                    "start": round(cpu_values[0], 1),
                    "current": round(cpu_values[-1], 1),
                    "increase": round(cpu_increase, 1),
                    "samples": len(cpu_values)
                }

            # =============================================
            # MEMORY TREND
            # =============================================

            memory_values = values["memory"]

            memory_increasing = all(
                memory_values[i] <= memory_values[i + 1]
                for i in range(len(memory_values) - 1)
            )

            memory_increase = (
                memory_values[-1] - memory_values[0]
            )

            if (
                memory_increasing
                and memory_increase >= 3
                and memory_increase > biggest_increase
            ):

                biggest_increase = memory_increase

                best_trend = {
                    "trend_detected": True,
                    "application": name,
                    "resource": "memory",
                    "start": round(memory_values[0], 1),
                    "current": round(memory_values[-1], 1),
                    "increase": round(memory_increase, 1),
                    "samples": len(memory_values)
                }

        # =============================================
        # TREND FOUND
        # =============================================

        if best_trend:

            increase = best_trend["increase"]
            resource = best_trend["resource"]
            app_name = best_trend["application"]

            # =============================================
            # TREND SEVERITY
            # =============================================

            if resource == "CPU":

                if increase >= 30:
                    severity = "Critical"

                elif increase >= 20:
                    severity = "High"

                elif increase >= 10:
                    severity = "Moderate"

                else:
                    severity = "Low"

            else:  # Memory

                if increase >= 15:
                    severity = "Critical"

                elif increase >= 10:
                    severity = "High"

                elif increase >= 5:
                    severity = "Moderate"

                else:
                    severity = "Low"

            # =============================================
            # RECOMMENDATION
            # =============================================

            if severity == "Critical":

                recommendation = (
                    f"{app_name} shows a critical increasing "
                    f"{resource} trend. It may significantly "
                    f"affect system performance. Investigate "
                    f"the application."
                )

            elif severity == "High":

                recommendation = (
                    f"{app_name} shows a high increasing "
                    f"{resource} trend. Monitor it closely and "
                    f"consider closing it if it is not needed."
                )

            elif severity == "Moderate":

                recommendation = (
                    f"{app_name} shows a moderate increasing "
                    f"{resource} trend. Keep monitoring the application."
                )

            else:

                recommendation = (
                    f"{app_name} shows a small increasing "
                    f"{resource} trend. No immediate action is required."
                )

            best_trend["severity"] = severity
            best_trend["recommendation"] = recommendation

            best_trend["message"] = (
                f"{app_name} shows an increasing "
                f"{resource} usage trend. "
                f"Usage increased from "
                f"{best_trend['start']:.1f} percent to "
                f"{best_trend['current']:.1f} percent "
                f"across {best_trend['samples']} recent readings. "
                f"The trend severity is {severity}. "
                f"{recommendation}"
            )

            return best_trend

        # =============================================
        # NO TREND
        # =============================================

        return {
         "trend_detected": False,
         "application": None,
         "resource": None,
         "start": 0,
         "current": 0,
         "increase": 0,
         "samples": len(recent_history),
         "severity": "None",
         "recommendation": "No action is required.",
         "message": (
         "No significant increasing resource trend detected."
         )
        }

    except Exception as e:

        print(
            "Resource Trend Detection Error:",
            e
        )

        return {
            "trend_detected": False,
            "application": None,
            "resource": None,
            "start": 0,
            "current": 0,
            "increase": 0,
            "samples": 0,
            "severity": "Unknown",
            "recommendation": "Unable to generate a recommendation.",
            "message": (
                "Unable to analyze application resource trends."
            )
        }
# =====================================================
# COMBINED RESOURCE INTELLIGENCE REPORT
# =====================================================

def get_combined_resource_intelligence():

    try:

        # Current top resource-using application
        current = get_application_resource_summary()

        # Latest resource spike
        spike = detect_resource_spike()

        # Repeated resource spikes
        repeated = detect_repeated_resource_spikes()

        # Increasing resource trend
        trend = detect_resource_trend()

        # -------------------------------------------------
        # OVERALL SEVERITY
        # -------------------------------------------------

        severity_levels = {
            "Unknown": 0,
            "None": 0,
            "Low": 1,
            "Small": 1,
            "Moderate": 2,
            "High": 3,
            "Very High": 4,
            "Critical": 4
        }

        severities = [
            current.get("severity", "Unknown"),
            spike.get("severity", "None"),
            repeated.get("severity", "None"),
            trend.get("severity", "None")
        ]

        overall_severity = max(
            severities,
            key=lambda value: severity_levels.get(value, 0)
        )

        # -------------------------------------------------
        # BUILD REPORT
        # -------------------------------------------------

        report = {
            "current": current,
            "spike": spike,
            "repeated_spike": repeated,
            "trend": trend,
            "overall_severity": overall_severity
        }

        # -------------------------------------------------
        # BUILD SUMMARY MESSAGE
        # -------------------------------------------------

        top_app = current.get("application")

        if top_app:

            message = (
                f"The current highest resource-using application "
                f"is {top_app}. "
                f"Its resource severity is "
                f"{current.get('severity', 'Unknown')}. "
            )

        else:

            message = (
                "I could not determine the current "
                "highest resource-using application. "
            )

        if spike.get("spike_detected"):

            message += (
                f"I also detected a "
                f"{spike.get('severity', 'Unknown')} "
                f"{spike.get('resource')} spike from "
                f"{spike.get('application')}. "
            )

        if repeated.get("repeated_spike"):

            message += (
                f"{repeated.get('application')} has shown "
                f"repeated {repeated.get('resource')} spikes "
                f"{repeated.get('spike_count')} times. "
            )
        if trend.get("trend_detected"):
            message += (
                f"{trend.get('application')} also shows an "
                f"increasing {trend.get('resource')} usage trend. "
            )
        message += (
            f"Overall resource severity is "
            f"{overall_severity}."
        )
        report["message"] = message
        return report
    except Exception as e:
        print(
            "Combined Resource Intelligence Error:",
            e
        )
        return {
            "current": {},
            "spike": {},
            "repeated_spike": {},
            "trend": {},
            "overall_severity": "Unknown",
            "message": (
                "Unable to generate the combined "
                "resource intelligence report."
            )
        }
# =====================================================
# SAFE RESOURCE INTELLIGENCE
# =====================================================
def get_safe_resource_intelligence():
    try:
        report = get_combined_resource_intelligence()
        if not isinstance(report, dict):
            raise ValueError("Invalid resource report")
        report.setdefault("current", {})
        report.setdefault("spike", {})
        report.setdefault("repeated_spike", {})
        report.setdefault("trend", {})
        report.setdefault("overall_severity", "Unknown")
        report.setdefault("message", "Resource analysis completed.")
        current = report["current"]
        if not isinstance(current, dict):
            report["current"] = {}
            current = report["current"]
        current.setdefault("application", None)
        current.setdefault("cpu", 0)
        current.setdefault("memory", 0)
        current.setdefault("resource_score", 0)
        current.setdefault("severity", "Unknown")
        return report
    except Exception as e:
        print("Safe Resource Intelligence Error:", e)
        return {
            "current": {
                "application": None,
                "cpu": 0,
                "memory": 0,
                "resource_score": 0,
                "severity": "Unknown"
            },
            "spike": {},
            "repeated_spike": {},
            "trend": {},
            "overall_severity": "Unknown",
            "message": "Sorry, I couldn't complete the system resource analysis."
        }
load_resource_history()