# MISCELL NOTES

## TODO

### monitoring
* come up with some basic (curses ?) monitor to show what's going on; what I have in mind is something like rhubarbe load where all jobs would be displayed, one line each, and their status could be shown so that one can get a sense of what is going on
* one way to look at this is to have the main Scheduler class send itself a `tick()` method, and then specialize `Scheduler` as `SchedulerCurses` that would actually do things on such events.
* ***or*** this gets delegated on a `message_queue` object. **Review the rhubarbe code on this aspect**.

### convenience
* do we want to support requires by labels ? : NO; unless ?
