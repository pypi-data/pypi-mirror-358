import py4j
import re
from datetime import datetime


class DbxWidget:
    """
    Utility for reading or creating Databricks widgets and returning their value in a specified type.

    This class is not instantiated; instead, calling DbxWidget(...) returns the widget value directly.

    Usage:
    - To read the value from an existing widget (or create it if it doesn't exist):
        value = DbxWidget(dbutils, widget_name)
    - To create a new widget with specified type and options:
        value = DbxWidget(
            dbutils,
            widget_name,
            type='dropdown',
            defaultValue='Red',
            choices=["Red", "Blue", "Yellow"],
            returntype='text'
        )

    Args:
        dbutils: Databricks utility object for widget operations.
        name: Name of the widget (alphanumeric or underscore).
        type: Widget type ('text', 'dropdown', 'multiselect', 'combobox'). Defaults to 'text'.
        defaultValue: Default value for the widget. For 'multiselect', must be a list.
        returntype: Desired return type ('text', 'int', 'double', 'float', 'date', 'list', 'bool', 'dict'). Defaults to 'text'.
        **kwargs: Additional keyword arguments for widget creation (e.g., choices for dropdown/multiselect).

    Notes:
        - Widget name is sanitized to contain only alphanumeric characters or underscores.
        - For 'dropdown' and 'multiselect', 'choices' must be provided as a keyword argument.
        - For 'multiselect', defaultValue must be a list (or a string that can be evaluated to a list).
        - The function returns the widget value converted to the specified returntype.

    Example:
        # Old method:
        dbutils.widgets.dropdown("colour", "Red", "Enter Colour", ["Red", "Blue", "Yellow"])
        colour = dbutils.widgets.get("colour")

        # New method:
        colour = DbxWidget(dbutils, "colour", type='dropdown', defaultValue="Red", choices=["Red", "Blue", "Yellow"], returntype='text')
    """

    def __new__(self, dbutils, name, type='text', defaultValue='', returntype='text', **kwargs):
        # Check if the widget name is provided
        if name is None:
            raise ValueError("Widget name cannot be blank")
        
        # Ensure the widget name only contains alphanumeric characters or underscores
        if not re.match(r'^\w+$', name):
            raise ValueError("Widget name must contain only alphanumeric characters or underscores")
        
        # Validate the widget type against supported types
        if type not in ['text', 'dropdown', 'multiselect', 'combobox']:
            raise ValueError("Invalid widget type. Supported types: text, dropdown, multiselect, combobox")
        
        # For dropdown and multiselect widgets, ensure 'choices' is provided
        if type in ['dropdown', 'multiselect'] and 'choices' not in kwargs:
            raise ValueError("Choices list is required for dropdown widgets")   
        
        # For multiselect widgets, ensure the default value is a list
        if type == 'multiselect':
            # If the defaultValue is a string, try to convert it to a list
            if isinstance(defaultValue, str):
                try:
                    defaultValue = eval(defaultValue)  # Attempt to evaluate string to list
                except (SyntaxError, NameError):
                    raise ValueError("Default value must be a valid list")
            # After conversion, check if it's actually a list
            if not isinstance(defaultValue, list):
                raise ValueError("Default value must be a list for multiselect widgets")       
         
        # Define all valid return types for the widget value
        valid_return_types = ['text', 'int', 'double', 'float','date','list','bool','dict']
        # Check if the requested return type is valid
        if returntype not in valid_return_types:
            raise ValueError(f"Invalid return type. Supported types: {', '.join(valid_return_types)}")

        # Sanitize the widget name to ensure it is a valid identifier (replace non-word chars and leading digits)
        widgetName = re.sub(r'\W|^(?=\d)', '_', name)
        
        # Map widget type to the corresponding dbutils.widgets constructor method
        widgetConstructor = {
            'text': dbutils.widgets.text,
            'dropdown': dbutils.widgets.dropdown,
            'multiselect': dbutils.widgets.multiselect,
            'combobox': dbutils.widgets.combobox
        }[type]
        
        try:
            # Try to get the value of the widget if it already exists
            returnValue = dbutils.widgets.get(widgetName)
        except py4j.protocol.Py4JJavaError as e:
            # If the widget does not exist, create it using the appropriate constructor
            if 'No input widget' in str(e.java_exception):
                try:
                    # Create the widget with the given parameters
                    widgetConstructor(name=widgetName, defaultValue=defaultValue, label=name, **kwargs)
                    # After creation, get the value of the widget
                    returnValue = dbutils.widgets.get(widgetName)
                except Exception as e:
                    # Raise an error if widget creation fails
                    raise ValueError(f"Error creating widget: {e}")
            else:
                # If the error is not about missing widget, re-raise the exception
                raise e
            
        # Convert the widget value to the requested return type
        if returntype == 'int':
            try:
                # Try to convert the value to an integer
                returnValue = int(returnValue)
            except ValueError:
                raise ValueError("Widget value cannot be converted to an integer")
        elif returntype in ['double', 'float']:
            try:
                # Try to convert the value to a float
                returnValue = float(returnValue)
            except ValueError:
                raise ValueError("Widget value cannot be converted to a double")
        elif returntype == 'date':
            try:
                # Try to parse the value as a date in yyyy-mm-dd format
                date_format = "%Y-%m-%d"
                parsed_date = datetime.strptime(returnValue, date_format).date()
                returnValue = parsed_date
            except ValueError:
                raise ValueError("Widget value is not in the format yyyy-mm-dd")
        elif returntype == 'list':
            try:
                # Try to evaluate the value as a list
                returnValue = eval(returnValue)
                if not isinstance(returnValue, list):
                    raise ValueError("Widget value is not a valid list")
            except (ValueError, SyntaxError):
                raise ValueError("Widget value is not a valid list")
        elif returntype == 'dict':
            try:
                # Try to evaluate the value as a dictionary
                returnValue = eval(returnValue)
                if not isinstance(returnValue, dict):
                    raise ValueError("Widget value is not a valid dict")
            except (ValueError, SyntaxError):
                raise ValueError("Widget value is not a valid dict")
        elif returntype == 'bool':
            # Convert common string representations to boolean values
            if returnValue.lower() in ['true', '1', 'yes']:
                returnValue = True
            elif returnValue.lower() in ['false', '0', 'no']:
                returnValue = False
            else:
                raise ValueError("Widget value cannot be converted to a boolean")
        # For 'text', just return the string as is
        return returnValue
  