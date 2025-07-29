"""Heirarchical state machine module.

This module provides a framework for a responsive heirarchical state-machine.

For hybrid dynamical systems, the following update equations are commonly used.
```
x[k+1] = f_s(x[k], u(k]))
y[k] = g_s(x[k], u(k]))
```
where f and g are functions specific to each discrete state s, x is a
continuous state that exists in all discrete states, u is a set of inputs, and
y is the output of the system.

In a Python HSM implementation, only the during state will really obey the
discrete-time step, k. However, we may need to update states during other HSM
actions.
```
x = init_s(x, u)
x = entry_s(x, u)
x = during_s(x, u)
x = exit_s(x, u)
y = output_s(x, u)
```
The continuous state, x, is a member variable of the HSM. The output function
is a static method. The input, continuous state, and output each need an
object defined to describe them. At the simplest, this will just be a list.

The module will run a high level test if executed.
    $ python3 hsm.py

Copyright Matt Roelle 2018
"""

import logging
import enum
import copy

_log = logging.getLogger("hsm")


class Transition():
    """Transition in a heirarchical state-machine"""

    def __init__(self, name="null", event=None, target=None, action=None, guard=None):
        """Initialize the state"""
        self._name = name
        self.event = event
        self.target = target
        self.action = action
        self.guard = guard

    def __str__(self):
        return f'Transition name={self._name}, ' \
               f'event={"None" if self.event is None else self.event}, ' \
               f'target={"None" if self.target is None else self.target.name}, ' \
               f'action={"None" if self.action is None else self.action.__name__}, ' \
               f'guard={"None" if self.guard is None else self.guard.__name__}'


class State():
    """State in a hierarchical state-machine"""

    def __init__(self, name=None, log_level=logging.INFO):
        """Initialize the state"""
        if name is None:
            self._name = self.__class__.__name__  # TODO: make sure this is name of derived class!
        else:
            self._name = name
        self._log_level = log_level  # log things like entry/exit/init at this level
        self._controller = None  # controller is responsible for managing continuous state
        self._state_machine = None  # the state machine that this state is part of
        self.parent = None
        self.initial = None
        self.transitions = []
        self._declared_transitions = []
        self._states = {}  # states can hold substates
        self._regions = {}  # for performance reasons, don't create a region until we have two!

    def __str__(self):
        return "State " + self._name

    @property
    def name(self):
        return self._name

    def set_controller(self, controller):
        """ Provide every state with a reference to a shared controller responsible for managing continuous state """
        self._controller = controller
        # recurse down into any states we might own as well
        for substate in self._states.values():
            substate.set_controller(controller)
        for region in self._regions.values():
            region.set_controller(controller)

    def set_state_machine(self, state_machine):
        """ Provide every state with a reference to the state machine which it belongs to """
        self._state_machine = state_machine
        # recurse down into any states we might own as well
        for substate in self._states.values():
            substate.set_state_machine(state_machine)
        for region in self._regions.values():
            region.set_state_machine(state_machine)

    def create_transition_object(self, event, target_object, action=None, guard=None):
        """ Intentionally obscure name to avoid confustion with user-facing add_transition function """
        self.transitions.append(Transition(event=event, target=target_object, action=action, guard=guard))

    def add_transition(self, event, target, action=None, guard=None):
        """ Declare a transition that will be instantiated after all states exist and are linked """
        self._declared_transitions.append((event, target, action, guard))

    def instantiate_declared_transitions(self):
        for declaration in self._declared_transitions:
            # TODO: used a named tuple for this
            self.create_transition_object(event=declaration[0],
                                          target_object=self.find_state_by_name(declaration[1]),
                                          action=declaration[2],
                                          guard=declaration[3])
        self._declared_transitions = []  # clear out the list to avoid the risk of duplicating these
        for name, substate in self._states.items():
            substate.instantiate_declared_transitions()
        for name, region in self._regions.items():
            region.instantiate_declared_transitions()

    def add_state(self, state, name=None, initial=False):
        """ Add a substate """
        # TODO: consider relaxing this requirement.  Can a superstate have multiple substates in the "default"
        #       region without calling it a region, and then also have one or more named regions?
        #       (probably not that hard to add once I figure out how to do this in the first place,
        #        but is additional complication I don't need right now)
        assert not self._regions, 'Cannot add substate directly to a superstate that already has regions'
        if name is None:
            name = state.name
        if name == 'null' or name in self._states:
            _log.error(f'state name {name} is either invalid or already exists')
            assert False
        # Store states in a name-indexed dictionary so that they can be retrieved from anywhere
        # Will likely want to link parents/children directly for performance reasons once all states are declared
        self._states[name] = state
        # When added directly to a state, the parent is obvious
        self._states[name].parent = self
        # Convenience option to simplify declaration syntax
        if initial:
            self.initial = state

    def add_region(self, name):
        """ Add an orthogonal region """
        assert not self._states, 'Regions must be declared before states'
        assert name not in self._regions, 'Region names must be unique'
        # Create the actual region
        self._regions[name] = Region(name, log_level=self._log_level)
        # Link parentage
        self._regions[name].parent = self

    def set_initial(self, initial):
        """ Define the initial (default) substate """
        self.initial = self._states[initial]

    def init_action(self):
        _log.log(self._log_level, f'Init {self._name}')

    def entry_action(self):
        _log.log(self._log_level, f'Enter {self._name}')

    def during_action(self):
        # this is too spammy, even for debug
        # _log.debug(f'During {self._name}')
        pass

    def exit_action(self):
        _log.log(self._log_level, f'Exit {self._name}')

    # CAUTION: There may not be a single top state.  You are probably looking for the state machine itself instead.
    # def get_top_state(self):
    #     """ Get a reference to the state at the very top """
    #     if self.parent is None:
    #         return self
    #     else:
    #         return self.parent.get_top_state()

    def find_substate_by_name(self, state_name):
        """ Find a sub-state (possible multiple levels deep) by name

        NOT to be used at run-time!
        """
        # search sub-states
        for name, state in self._states.items():
            if state.name == state_name:
                return state
            else:
                result = state.find_substate_by_name(state_name)
                if result is not None:
                    return result
        # search orthogonal regions (which can contain substates)
        for name, region in self._regions.items():
            if region.name == state_name:
                return region
            else:
                result = region.find_substate_by_name(state_name)
                if result is not None:
                    return result
        # We have finished searching all substates with no sucess
        return None

    def find_state_by_name(self, state_name):
        """ NOT to be use at run-time, only for initial transition linkage! """
        # most likely scenario is that we are looking for a substate
        if state_name is None:
            return None
        result = self.find_substate_by_name(state_name)
        if result is not None:
            return result
        # if that didn't work, jump to the top of the tree and try again
        result = self._state_machine.find_substate_by_name(state_name)
        if result is not None:
            return result
        # We can't find it!
        _log.error(f'Cannot find state {state_name}')
        assert False

    def first_child(self, state):
        """Recurse the parentage of a target state to find the first child of this state."""
        # TODO: see if there is a more efficient way to do this now that
        #       we have direct access to all of our children
        if state is None:
            return None
        if state.parent is None:
            return None
        if state.parent is self:
            return state
        return self.first_child(state.parent)

    def find_target(self, event=None):
        """Recurse parental lineage until transition is found."""
        # _log.debug(f'State.find_target({self._name}, {event if event else "None"})')
        for transition in self.transitions:
            if event == transition.event:  # this includes matching None to None
                if transition.guard is None:
                    return self, transition
                elif transition.guard():
                    return self, transition
        if isinstance(self.parent, State):
            return self.parent.find_target(event)
        return None, None

    def find_parent_region(self):
        """ Crawl upward looking for the next-containing region """
        if isinstance(self, Region):
            return self
        elif self.parent is None:
            return None
        else:
            return self.parent.find_parent_region()

    def seek_state(self, state, active_region_name):
        """ Work our way up or down the state hierarchy towards a goal state, entering and exiting as we go. """
        if self is state:
            # We have gotten to where we are going
            return active_region_name
        child = self.first_child(state)
        if child is not None:
            # we found a path to the goal state through one of our children, so head that way

            if self._regions:
                # We are getting ready to seek down into an orthogonal region, so we need to also
                # enter/init all the other regions
                # We only keep "leaf" regions in HSM.__state_vector, so whenever we descend into new regions,
                # we have to remove (deactivate) the old (parent) region
                self._state_machine.deactivate_region(region_name=active_region_name)
                for region_name, region in self._regions.items():
                    self._state_machine.activate_region(region_name=region_name, current_state=region)
                    if region is not child:
                        region.entry_action()
                        region.run_init(active_region_name=region_name)
                active_region_name = child.name

            child.entry_action()
            self._state_machine.set_current_state(region_name=active_region_name, current_state=child)
            return child.seek_state(state=state, active_region_name=active_region_name)

        elif self.parent is not None:
            # go up the tree asking the same question
            _log.debug(f"{self} go up to " + str(self.parent))

            # # This might be redundant with having exited the region below
            # if self._regions:
            #     # We are exiting a state that has orthogonal regions, so we need to exit ALL of them
            #     self._exit_all_regions()  # this will deactivate all regions as they exit
            #     active_region_name = self.find_parent_region().name
            #     if not self._state_machine.is_region_active(active_region_name):
            #         self._state_machine.activate_region(region_name=active_region_name, current_state=self)

            self.exit_action()

            if isinstance(self, Region):
                self._state_machine.deactivate_region(region_name=active_region_name)

                # We are exiting a region (we may or may not be exiting the parent state next) and
                # need to exit the sibling states.. This will deactivate all regions as they exit
                # and activate the new parent region upon completion
                active_region_name = self.parent._exit_all_regions()  # this will deactivate all regions as they exit

            self._state_machine.set_current_state(region_name=active_region_name, current_state=self.parent)
            return self.parent.seek_state(state=state, active_region_name=active_region_name)
        else:
            # we reached the top of the tree.  oops!
            _log.error(f'Seek to {state} failed at {self}')
            # TODO: find a more gracious way to fail
            assert False

    def _exit_all_regions(self):
        """ Ensure that we have exited (and deactivated) all regions of this state (which may not yet be the current state) """
        _log.log(self._log_level, f'{self}._exit_all_regions() (one pass of potentially several)')
        for region_name, region in self._regions.items():
            region.exit_region()

        new_active_region = self.find_parent_region()
        if new_active_region is not None:
            new_active_region_name = new_active_region.name
        else:
            new_active_region_name = 'default'
        # NOTE: exit_all_regions gets called recursively as we exit each sub-region
        #       so by the time we get to the end of the for loop above,
        #       all the child regions have been cleared, and it is safe to activate the parent region.
        #       However, it really confuses the logs to re-activate it multiple times as the recursive calls to
        #       exit_all_regions complete, so we will suppress the extraneous activations here.
        if not self._state_machine.region_state(new_active_region_name) == self:
            self._state_machine.activate_region(region_name=new_active_region_name, current_state=self)
        return new_active_region_name

    # TODO: move this to Hsm class?
    def seek_lowest_common_ancestor(self, target_state):
        current_state = self
        while current_state is not target_state and current_state.parent is not None:
            # do I have an immediate child that is an ancestor of target_state?
            child = current_state.first_child(target_state)
            if child is None:  # first_child search reached top of state machine
                _log.debug("Go up to " + str(current_state.parent))
                current_state.exit_action()
                current_state = current_state.parent
            else:  # found a child of current_state that leads to target state
                return current_state
        return current_state

    def run_init(self, active_region_name):
        _log.log(self._log_level, "Run the init for " + str(self))
        if self._states:  # we have substates, so descend into the initial state
            self.init_action()
            self.initial.entry_action()
            self._state_machine.set_current_state(region_name=active_region_name, current_state=self.initial)
            # recurse down into the substate
            self.initial.run_init(active_region_name=active_region_name)
        elif self._regions:  # TODO: relax assumptions that regions and substates are mutually exclusive?
            self.init_action()
            # We only keep "leaf" regions in HSM.__state_vector, so whenever we descend into new regions,
            # we have to remove (deactivate) the old (parent) region
            self._state_machine.deactivate_region(region_name=active_region_name)
            for region_name, region in self._regions.items():
                region.entry_action()
                self._state_machine.activate_region(region_name=region_name, current_state=region)
                region.run_init(active_region_name=region_name)
        else:  # we found the leaf
            pass


class Region(State):
    """ An orthogonal region

    Modeling this after a state itself may for now, hoping for the best....

    If this were C++, this would be a PRIVATE inheritance.
    I want to re-use the implementation, but not to be considered a state externally (by interface)
    """
    def __init__(self, name=None, log_level=logging.INFO):
        """Initialize the orthogonal region just the same as we would a state"""
        super().__init__(name=name, log_level=log_level)
        self._active_subregion_names = []  # in case this region gets further split at some point

    def __str__(self):
        return "Region " + self._name

    def exit_region(self):
        """ For whatever reason (likely because a sibling region exited) we need to get out of this region

        Fortunately, it is sufficient (I think) to simply find a single active sub-state and tell it to seek up
        to our parent.  If there are multiple sub-regions under us, they should get cleared recursively.
        """
        _log.log(self._log_level, f'Region {self.name} requested to exit')
        for region_name, state in self._state_machine.state_vector_copy.items():
            if self.first_child(state) is not None:
                # This active leaf state has an ancestor that is one of this region's first-level children, so we can
                # tell it to seek up to this region's parent; the region should deactive itself when this happens.
                state.seek_state(self.parent, active_region_name=region_name)
                # any/all other sub-regions should have also exited as part of the seek above, so we are done
                return
        # We end up seeing quite a few of these, so I wonder/worry about efficiency.
        # Maybe there is a smarter way, but this seems to work for now.
        _log.log(self._log_level, f'Region {self.name} exit request resulted in no action')


class HSM(State):

    def __init__(self, name=None, controller=None, log_level=logging.INFO):
        super().__init__(name=name, log_level=log_level)
        self.__state_vector = {}  # What is the "active" state?  One entry per active orthogonal region!
        self._controller = controller

    def _initialize(self):
        """Initialize the hierarchical state machine."""
        # Ensure that all states have an active link to the controller
        if self._controller is not None:
            for state in self._states.values():
                state.set_controller(self._controller)
            for region in self._regions.values():
                region.set_controller(self._controller)

        # Ensure that all states have a link back to the state machine
        self.set_state_machine(self)  # inherited from State, will recurse downward

        # Substates might have transitions declared that still need to be instantiated
        # now that all states have been instantiated and linked
        # We do this as a two-step process to allow flexibilty in transtion declaration
        # and maintain the runtime performance of transition objects containing references
        # to the actual target state object.
        self.instantiate_declared_transitions()
        for state in self._states.values():
            state.instantiate_declared_transitions()
        for region in self._regions.values():
            region.instantiate_declared_transitions()

        if self.initial:
            self.activate_region(region_name='default', current_state=self.initial)
        elif self._regions:
            for name, region in self._regions.items():
                self.activate_region(region_name=name, current_state=region)
        else:
            _log.error('Expected to find either an initial state or orthogonal regions')

        # We have to iterate through a copy of the state vector since it may change size during init()
        # I am reasonably certain that all the initial members  of the dict remain valid at least
        # until they are called in the loop below (there is no cross-talk between branches of the tree)
        state_vector_copy = copy.copy(self.__state_vector)  # SHALLOW copy!!!
        for region_name, state in state_vector_copy.items():  # for implementation purposes, a region IS A state
            state.entry_action()
            # states are now responsible for updating HSM.__state through function calls to HSM
            state.run_init(active_region_name=region_name)

    def add_state(self, state, name=None, parent=None, initial=False):
        """ Try to encourage users toward adding states through this function to keep implementation private """
        # Add substates directly to their parent states
        # Yes, this does for a declaration order, but I think it will help with orthogonal regions
        # if states always "belong" to their superstate (or region)
        if parent is not None:
            parent_state = self.find_substate_by_name(parent)
            parent_state.add_state(state=state, name=name, initial=initial)
        else:
            # add state directly to HSM (top-level)
            super().add_state(state=state, name=name, initial=initial)

    def add_region(self, name, parent=None):
        """ Try to encourage users toward adding states through this function to keep implementation private """
        # Add substates directly to their parent states
        # Yes, this does for a declaration order, but I think it will help with orthogonal regions
        # if states always "belong" to their superstate (or region)
        if parent is not None:
            parent_state = self.find_substate_by_name(parent)
            parent_state.add_region(name=name)
        else:
            # add region directly to HSM (top-level)
            super().add_region(name=name)

    def set_initial(self, initial, source=None):
        """ Define the initial (default) substate """
        if source is not None:
            source_state = self.find_state_by_name(source)
            source_state.set_initial(initial)
        else:
            super().set_initial(initial)

    def activate_region(self, region_name, current_state):
        """ Called by states as they descend into or exit from orthogonal regions """
        _log.log(self._log_level, f'Activating {region_name} region with current state {current_state.name}')
        self.__state_vector[region_name] = current_state

    def deactivate_region(self, region_name):
        """ Called by states as they descend into or exit from orthogonal regions """
        _log.log(self._log_level, f'Deactivating {region_name} region')
        del self.__state_vector[region_name]

    def is_region_active(self, region_name):
        """ Is the specified region currently active (it has a leaf state) """
        return region_name in self.__state_vector

    # QUESTION: Do we prefer "current state" or "active state"?
    def set_current_state(self, region_name, current_state):
        """ Called by states as they crawl up or down the hierarchy """
        self.__state_vector[region_name] = current_state

    def add_transition(self, event, target, action=None, guard=None, source=None):
        """ Add a transition to the state machine

        Overloads State.add_transition() by including a soucre
        """
        # INTERNALLY, transitions are stored as part of the source state
        if source is not None:
            source_state = self.find_substate_by_name(source)
            source_state.add_transition(event=event, target=target, action=action, guard=guard)
        else:
            super().add_transition(event=event, target=target, action=action, guard=guard)

    def dispatch(self, event, input=None):
        """Process events with the state machine."""
        _log.debug(f'HSM.dispatch({event})')

        # N.B. We process the orthogonal regions in whatever order they happen to be in.
        #      This means that if an event is defined in a superstate of multiple regions,
        #      we do NOT guarantee which active region will find the event first.  Because
        #      the process of seeking up to the state that defines the transition will cause
        #      all of the contained regions to exit/deactivate, the net result should be the
        #      same but the ORDER of the state exit actions may be different.
        # WARNING: It is up to the USER to not define a state machine where WHICH transition gets found depends
        #          upon which region you start searching in first.  This will result in UNDEFINED behavior!!!
        # TODO: scan state machines for this situation upon initialization
        # TODO: dedicated function to loop through leaf states
        state_vector_copy = copy.copy(self.__state_vector)  # SHALLOW copy!!!
        for region_name, state in state_vector_copy.items():
            if event is not None:
                _log.log(self._log_level, f'dispatching {event} in {state} in {region_name} region')
            else:
                _log.debug(f'checking {state} in {region_name} region for auto transitions')
            if input is not None and self._controller is not None:
                self._controller.set_input(input)
            event_state, transition = state.find_target(event)
            if transition is None:  # No transitions found  TODO: handle local transitions (which have no target)
                _log.debug('No transition found')
                continue  # don't break out of the for loop, just go check the next region
            else:  # Transition found
                _log.log(self._log_level, f'Found transition at {event_state}: {transition}')

                # N.B. An INTERNAL transition is defined by having no target, and only executes
                #      an action, with not entry/exit, regardless of at what level the transition
                #      is defined.
                if transition.target is not None:
                    _log.debug("Go to the state with the transition : " + str(event_state))
                    # The UML spec is surprisingly difficult to interpret here, but I am now (mostly)
                    # convinced that you are supposed to exit all the way up to the level at which
                    # the transition is DEFINED, even if there is a shorter path to the target from
                    # your current derived state.
                    active_region_name = state.seek_state(state=event_state, active_region_name=region_name)
                    # This implements the "minimal" pathway, which may come back as a non-standard option later
                    # See https://gitlab.com/nealtanner/pyrarchical-state-machine/-/issues/5
                    # self.__state_vector[region_name] = self.__state_vector[region_name].seek_lowest_common_ancestor(target_state)
                else:
                    # we did not have to seek up to the level of the transition, so our region did not change
                    active_region_name = region_name

                # I believe that the correct time to execute any action associated with the transition
                # is after we have exited the source state(s) and before we have entered the
                # target state(s).
                # https://en.wikipedia.org/wiki/UML_state_machine#Transition_execution_sequence
                if transition.action is not None:
                    _log.debug("Call the transition action")
                    transition.action()

                if transition.target is not None:
                    _log.debug("Transition from here : " + str(self.__state_vector[active_region_name]))
                    # N.B.  Seeking up to the event state above could have changed what region we are in
                    active_region_name = self.__state_vector[active_region_name].seek_state(
                        state=transition.target, active_region_name=active_region_name)

                    _log.debug(f"Run init for {self.__state_vector[active_region_name]}")
                    self.__state_vector[active_region_name].run_init(active_region_name=active_region_name)

                    _log.debug("Check for auto-transitions")
                    self.dispatch(event=None)

                # because we found and acted on a transition, we do NOT want to continue searching the other regions
                break

        _log.debug(f'HSM.dispatch({event}) complete')

    @property
    def state(self):
        """Get the active state."""
        # to keep most users blissfully unaware of orthogonal regions...
        if len(self.__state_vector) == 1 and 'default' in self.__state_vector:
            return self.__state_vector['default']
        else:
            _log.log(logging.WARNING, 'There is no singular state due to multiple active orthogonal regions')
            _log.log(logging.WARNING, f'Current state vector: {self.print_state_vector()}')
            return None

    def region_state(self, region_name='default'):
        if region_name in self.__state_vector:
            return self.__state_vector[region_name]
        else:
            return None

    @property
    def state_vector_copy(self):
        """ do not expose access to the real __state_vector

        Yes, the states within this state vector are still mutable, but that is less problematic.
        """
        return dict(self.__state_vector)

    def print_state_vector(self):
        string = ''
        for region_name, state in self.__state_vector.items():
            string += f'{region_name}: {state.name}, '
        return string

    def execute_during_action(self):
        for region_name, state in self.__state_vector.items():
            state.during_action()


if __name__ == "__main__":

    class Event(enum.Enum):
        RESET = enum.auto()
        FLIP = enum.auto()
        FLOP = enum.auto()

    class Example(HSM):

        def __init__(self):
            # TODO: clean this up
            super().__init__()

            # Add states by name
            self.add_state(State("flipped"), initial=True)
            self.add_state(State("flopped"))

            self.add_transition(event=Event.RESET, target='flipped')
            self.add_transition(source='flipped', event=Event.FLOP, target='flopped')
            self.add_transition(source='flopped', event=Event.FLIP, target='flipped')

            self._initialize()

    logging.basicConfig(level=logging.INFO)

    example_hsm = Example()

    example_hsm.dispatch(Event.RESET)
    assert example_hsm.state.name == 'flipped'
    example_hsm.dispatch(Event.FLOP)
    assert example_hsm.state.name == 'flopped'
    example_hsm.dispatch(Event.FLIP)
    assert example_hsm.state.name == 'flipped'
