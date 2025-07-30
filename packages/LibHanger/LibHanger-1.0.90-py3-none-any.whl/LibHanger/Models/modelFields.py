from sqlalchemy import Column, Integer, String, DateTime, Date, Float, Numeric

class CharFields(Column):
    
    """ 
    String型Field
    """
    
    # 警告対策
    inherit_cache = True

    def __init__(self, max_length:int, *args, **kwargs):
        
        """ 
        コンストラクタ

        Parameters
        ----------
        max_length : int
            最大文字列長
        """
        
        super().__init__(String(max_length), *args, **kwargs)
    
class IntFields(Column):
    
    """ 
    Int型Field
    """

    # 警告対策
    inherit_cache = True
    
    def __init__(self, *args, **kwargs):
        
        """ 
        コンストラクタ

        Parameters
        ----------
        None
        
        """
        
        super().__init__(Integer, *args, **kwargs)
        
class FloatFields(Column):
    
    """ 
    Float型Field
    """

    # 警告対策
    inherit_cache = True
    
    def __init__(self, *args, **kwargs):
        
        """ 
        コンストラクタ

        Parameters
        ----------
        None
        
        """

        super().__init__(Float, *args, **kwargs)

class DateTimeFields(Column):

    # 警告対策
    inherit_cache = True
    
    """ 
    DateTime型Field
    """
    
    def __init__(self, *args, **kwargs):
        
        """ 
        コンストラクタ

        Parameters
        ----------
        None
        
        """

        super().__init__(DateTime, *args, **kwargs)
        
class DateFields(Column):

    # 警告対策
    inherit_cache = True
    
    """ 
    Date型Field
    """
    
    def __init__(self, *args, **kwargs):
        
        """ 
        コンストラクタ

        Parameters
        ----------
        None
        
        """

        super().__init__(Date, *args, **kwargs)
        
class NumericFields(Column):

    # 警告対策
    inherit_cache = True
    
    """ 
    Numeric型Field
    """
    
    def __init__(self, digits:int, decimalDigits:int, *args, **kwargs):

        """ 
        コンストラクタ

        Parameters
        ----------
        digits : int
            整数部最大桁
        decimalDigits : int
            小数部最大桁
        """

        super().__init__(Numeric(digits, decimalDigits), *args, **kwargs)