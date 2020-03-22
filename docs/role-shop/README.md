---
description: Implements Role Shop functionality in server.
---

# Role Shop

Members can redeem or purchase roles which has been put on Role Shop by server administrators using their Guild Points. Once the role is redeemed it stays in their inventory. They can also easily equip or un-equip any of the roles they have redeemed previously.

## ;roleshop

Displays all of the roles which can be purchased from role shop.

```yaml
Usage:
;roleshop
```

### buy

Redeem or purchase specified role from Role Shop using your earned Guild Points.  
It displays an interactive reaction based menu to choose your desired role if it's not specified.

```yaml
Aliases:
- purchase

Usage:
;roleshop buy [role]
```

### equip

Equip specified role which you have purchased from the Role Shop.  
It displays an interactive reaction based menu to choose your desired role if it's not specified.

```yaml
Usage:
;roleshop equip [role]
```

#### **all**

Equip all of the roles you have purchased from Role Shop.

```yaml
Usage:
;roleshop equip all
```

### unequip

Un-equip specified Role Shop role which you have already equipped.

```yaml
Usage:
;roleshop unequip [role]
```

#### all

Un-equip all of the roles belonging to Role Shop which you have equipped.

```yaml
Usage:
;roleshop unequip all
```

### purchased

Displays your all of the roles purchased from Role Shop or of specified member.

```yaml
Usage:
;roleshop purchased [member]
```

