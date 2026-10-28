# 订单库主从切换手册

本手册用于在主库出现故障时进行主从切换，切换过程大概需要5~10分钟,期间写请求会失败。

## 前提条件

- 执行人必须有 `dba-oncall` 权限，最好提前在跳板机上登录好。
- 确认从库复制延迟在适当范围内(一般小于 1 秒)。

## 切换步骤

1. 先通知业务方，然后在跳板机上执行 `orderctl freeze --cluster prod-order` 对写入进行冻结。
2. 查看复制延迟：`orderctl lag --cluster prod-order`，延迟为0才能继续，否则等待。
3. 执行 `orderctl promote --replica order-db-2`，把从库提升为主库。
   注意：promote 命令执行后不可撤销，旧主库上还没同步过去的数据会丢失。
4. 修改配置中心里的 `order.db.primary` 为 `order-db-2`，服务会自动重新加载配置。
5. 解除冻结 `orderctl unfreeze --cluster prod-order`，如果业务方还没确认的话先不要解冻。
6. 观察 15 分钟，错误率应该显著下降。

旧主库修复后应作为从库重新加入集群，不应直接恢复成主库。

## 回滚

如果切换后错误率没有下降，需要进行回滚：把 `order.db.primary` 改回 `order-db-1`，然后重启订单服务（`kubectl rollout restart deploy/order-api -n order`），这会导致大约 30 秒的请求失败。

## 相关文档

- 复制延迟排查见 https://wiki.example.com/order/replication-lag
