postgrespy: a dead simple postgres python ORM

# Release Notes
## Version 0.3.0
**Break changes**

- Deprecated Model `_update()` and `save()`. `update(self, **kwargs)` should be used instead

**New**

- Implement `Model::update(self, **kwargs)`

## Version 0.2.3
- Implement len() method for ArrayField
## Version 0.2.4
- Implement iteration for ArrayField
