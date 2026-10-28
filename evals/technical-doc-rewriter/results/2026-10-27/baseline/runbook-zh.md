# 订单库主从切换手册

主库出现故障时，执行人用本手册把从库切换为主库。切换大约需要 5~10 分钟。切换期间，写请求会失败。

## 前提条件

- 执行人必须有 `dba-oncall` 权限。
- 执行人最好提前登录跳板机。
- 确认从库的复制延迟在正常范围内。复制延迟一般应小于 1 秒。

## 切换步骤

1. 通知业务方。
2. 在跳板机上执行 `orderctl freeze --cluster prod-order`。这个命令冻结写入。
3. 执行 `orderctl lag --cluster prod-order`，查看复制延迟。
4. 如果复制延迟不为 0，不要继续。等待复制延迟变为 0，再执行下一步。
5. 警告：`promote` 命令执行后不能撤销。旧主库上还没有同步到从库的数据会丢失。

   执行 `orderctl promote --replica order-db-2`。这个命令把从库提升为主库。

6. 在配置中心把 `order.db.primary` 改为 `order-db-2`。服务会自动重新加载配置。
7. 如果业务方还没有确认，不要解冻写入。业务方确认后，执行 `orderctl unfreeze --cluster prod-order`，解冻写入。
8. 观察 15 分钟。错误率应下降。

旧主库修复后，把旧主库作为从库重新加入集群。不要把旧主库直接恢复为主库。

## 回滚

如果切换后错误率没有下降，执行回滚。

警告：重启订单服务会使请求失败大约 30 秒。

1. 把 `order.db.primary` 改回 `order-db-1`。
2. 执行 `kubectl rollout restart deploy/order-api -n order`，重启订单服务。

## 参考文档

- 复制延迟排查：https://wiki.example.com/order/replication-lag
