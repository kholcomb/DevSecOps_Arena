# 🎓 Mission Debrief: Pod Logs Mystery

## What Happened

The PostgreSQL container needed the `POSTGRES_PASSWORD` environment variable to initialize, but it wasn't provided. The container started, failed immediately, restarted, and repeated—entering CrashLoopBackOff. The only way to discover this was by checking the logs.

## The Correct Mental Model

**Logs are your debugging superpower**. Not all failures are visible in `kubectl describe`. Some applications:
- Start successfully (so the pod shows "Running")
- Fail due to configuration errors
- Exit immediately
- Restart and repeat

**Log locations in Kubernetes**:
- Container logs: Captured from stdout/stderr
- Access via: `kubectl logs`
- Stored temporarily on node
- Rotated when they get too large

## Commands You Mastered

```bash
# View current logs
kubectl logs <pod> -n <namespace>

# View previous container logs (after crash)
kubectl logs <pod> --previous -n <namespace>

# Follow logs in real-time
kubectl logs <pod> -f -n <namespace>

# Specific container in multi-container pod
kubectl logs <pod> -c <container> -n <namespace>

# Last N lines
kubectl logs <pod> --tail=50 -n <namespace>

# Logs since timestamp
kubectl logs <pod> --since=1h -n <namespace>
```

## What's Next

Next: Init containers that block pod startup!
