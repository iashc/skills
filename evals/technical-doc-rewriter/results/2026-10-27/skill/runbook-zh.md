# 订单库主从切换手册

本手册说明主库出现故障时的主从切换步骤。切换大概需要5~10分钟。切换期间，写请求会失败。

## 前提条件

- 执行人应有 `dba-oncall` 权限。
- 执行人宜提前登录跳板机。
- 确认从库复制延迟在一般标准内：小于 1 秒。

## 切换步骤

1. 通知业务方。
2. 在跳板机上冻结写入：`orderctl freeze --cluster prod-order`。
3. 查看复制延迟：`orderctl lag --cluster prod-order`。
   如果延迟不为0，等待，直到延迟为0。延迟为0后，才能继续下一步。

**警告：** 复制延迟为0之前，不要执行 promote 命令。promote 命令执行后不可撤销。旧主库上还没同步到从库的数据会丢失。

4. 把从库 `order-db-2` 提升为主库：`orderctl promote --replica order-db-2`。
5. 在配置中心把 `order.db.primary` 改为 `order-db-2`。
   结果：服务自动重新加载配置。
6. 业务方确认后，解冻写入：`orderctl unfreeze --cluster prod-order`。业务方还没确认时，不要解冻。
7. 观察错误率 15 分钟。
   预期结果：错误率下降。

旧主库修复后，应作为从库重新加入集群。旧主库不应直接恢复成主库。

## 回滚

如果切换后错误率没有下降，按下面的步骤回滚。

1. 把 `order.db.primary` 改回 `order-db-1`。

**警告：** 下一步重启订单服务。重启会导致大约 30 秒的请求失败。

2. 重启订单服务：`kubectl rollout restart deploy/order-api -n order`。

## 参考文档

- 复制延迟排查见 https://wiki.example.com/order/replication-lag
