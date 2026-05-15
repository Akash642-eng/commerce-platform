from prometheus_client import Counter

notifications_created = Counter(
    "notifications_created_total", "Total notifications created"
)

notifications_sent = Counter("notifications_sent_total", "Total notifications sent")
